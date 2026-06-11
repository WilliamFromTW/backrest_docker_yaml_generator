import os
import sqlite3
from flask import Flask, render_template_string, request, flash, redirect, url_for, has_request_context
from ruamel.yaml import YAML

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_rclone_fields'

CONFIG_DIR = "docker-compose"
DB_PATH = os.path.join(CONFIG_DIR, "configs.db")
COMPOSE_FILE = os.path.join(CONFIG_DIR, "docker-compose.yml")
STARTUP_FILE = os.path.join(CONFIG_DIR, "startup.sh")
SHUTDOWN_FILE = os.path.join(CONFIG_DIR, "shutdown.sh")
RCLONE_FILE = os.path.join(CONFIG_DIR, "rclone.conf")

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)

# ==========================================
# 多國語系字典檔 (i18n)
# ==========================================
TRANSLATIONS = {
    'zh': {
        'title': '備份組態管理中樞',
        'tab_nodes': '遠端節點管理',
        'tab_scripts': '維運腳本 (啟動/停用)',
        'tab_restore': '還原說明 (Restore)',
        'global_settings': '系統全域設定 (Global Settings)',
        'ext_port': '外部 Port:',
        'global_mount': '宿主機全域掛載根目錄:',
        'tz_label': '時區 (TZ):',
        'apply_global': '套用全域設定',
        'hint_global': '💡 提示：修改或刪除節點後，請點擊上方按鈕手動更新實體檔案。新增節點會自動更新。',
        'add_node': '新增遠端連線節點',
        'cancel_edit': '取消編輯',
        'protocol': '通訊協定 (Protocol)',
        'node_name': '連線識別名稱 (作為目錄名)',
        'desc': '用途說明',
        'desc_ph': '例如：越南廠 SOP 圖檔每日備份',
        'ip': '伺服器 IP / Host',
        'port': '通訊埠 (Port)',
        'remote_path': '遠端路徑 (Remote Path)',
        'remote_path_ph': 'SharedFolder 或 /volume1/data',
        'username': '帳號 (Username)',
        'password': '密碼 (Password / Obscured)',
        'rclone_pass_hint': '💡 若為 Rclone SFTP，請填入 rclone obscure 加密後的密碼',
        'rclone_type': 'Rclone 類型 (type)',
        'rclone_type_ph': '例如: sftp, s3, drive',
        'rclone_args': 'Rclone 額外參數 (每行一個)',
        'rclone_args_ph': 'pubkey_file = /path/to/key\nuse_temp_mutime = false',
        'btn_save': '儲存節點資訊',
        'btn_update': '更新節點資訊',
        'btn_sync_files': '🔄 手動同步設定至檔案',
        'list_title': '現有連線節點清單',
        'col_proto': '協定',
        'col_name': '識別名稱',
        'col_ip': '遠端與本地掛載對應',
        'remote_target': '遠端來源',
        'local_path': '本地掛載點',
        'col_action': '操作',
        'btn_edit': '編輯',
        'btn_delete': '刪除',
        'confirm_del': '確定要刪除此節點嗎？',
        'no_nodes': '目前尚無任何連線設定。',
        'script_1_title': '1. 啟動腳本 (startup.sh)',
        'script_1_desc': '此腳本會先進行掛載，隨後才啟動 Docker 容器。',
        'fuse_hint': '⚠️ <b>Rclone 掛載提醒</b>：在 Linux (如 Ubuntu) 環境使用 Rclone 掛載時，宿主機需預先安裝 <code>fuse3</code> 或 <code>fuse</code> 相關套件。',
        'script_2_title': '2. 停用與卸載腳本 (shutdown.sh)',
        'script_2_desc': '此腳本會先停用 Docker 容器，再安全地卸載所有路徑。',
        'script_3_title': '3. docker-compose.yml',
        'btn_copy_script': '複製腳本',
        'btn_copy_yaml': '複製 YAML',
        'copied': '✅ 已複製',
        'flash_sync_ok': '✅ 實體檔案與腳本已成功同步更新！',
        'flash_global_db_only': '✅ 全域設定已更新於資料庫！請記得點擊「手動同步設定至檔案」來生效。',
        'flash_update_db_only': '✅ 節點「{name}」已更新於資料庫！請記得點擊「手動同步設定至檔案」來生效。',
        'flash_add_ok': '✅ 成功新增節點「{name}」！(實體檔案已自動同步更新)',
        'flash_name_err': '❌ 名稱「{name}」重複。',
        'flash_del_db_only': '🗑️ 節點已從資料庫移除！請點擊「手動同步設定至檔案」來生效。',
        'restore_card_title': 'Backrest 快照還原注意事項',
        'restore_path': '/data/dest/自訂目錄名稱',
        'restore_p1': '還原時請務必指定目標目錄：',
        'restore_p2': '⚠️ 目錄必須為空，否則還原會失敗。',
        'restore_p3': '還原後檔案位於宿主機 Volume: <code>backrest_data</code>。',
        'obscure_title': 'Rclone 密碼加密教學 (Obscure)',
        'obscure_p1': '若要使用 SFTP 等需要密碼的 Rclone 連線，請在宿主機終端機執行以下 Docker 指令產生加密密碼：',
        'obscure_cmd': "docker run --rm rclone/rclone:latest obscure '您的真實密碼'",
        'obscure_p2': '將終端機回傳的亂碼（例如 <code>v1M_...</code>）複製後，填入本系統的「密碼」欄位即可。',
        
        # 腳本內部翻譯
        'sh_start_mount': '=== 開始掛載遠端資料來源 ===',
        'sh_proc_node': '正在處理節點：',
        'sh_no_nodes': '(目前沒有設定任何節點)',
        'sh_mount_done': '掛載作業完成。',
        'sh_start_svc': '=== 啟動 Backrest 服務 ===',
        'sh_svc_done': '服務已啟動完畢！',
        'sh_stop_svc': '=== 停用 Backrest 服務 ===',
        'sh_start_umount': '=== 開始卸載遠端資料來源 ===',
        'sh_proc_umount': '正在卸載節點：',
        'sh_no_umount': '(目前沒有需要卸載的節點)',
        'sh_umount_done': '停用與卸載作業已全部完成！'
    },
    'en': {
        'title': 'Backup Config Hub',
        'tab_nodes': 'Remote Nodes',
        'tab_scripts': 'Ops Scripts',
        'tab_restore': 'Restore Guide',
        'global_settings': 'Global Settings',
        'ext_port': 'Ext Port:',
        'global_mount': 'Host Mount Root:',
        'tz_label': 'Timezone (TZ):',
        'apply_global': 'Apply',
        'hint_global': '💡 Hint: After editing or deleting, click "Sync Config to Files" above. New nodes sync automatically.',
        'add_node': 'Add Node',
        'cancel_edit': 'Cancel',
        'protocol': 'Protocol',
        'node_name': 'Identifier',
        'desc': 'Description',
        'desc_ph': 'e.g., Vietnam factory SOP daily backup',
        'ip': 'Host / IP',
        'port': 'Port',
        'remote_path': 'Remote Path',
        'remote_path_ph': 'SharedFolder or /volume1/data',
        'username': 'Username',
        'password': 'Password / Obscured',
        'rclone_pass_hint': '💡 For Rclone SFTP, use rclone obscure for password',
        'rclone_type': 'Rclone Type',
        'rclone_type_ph': 'e.g., sftp, s3',
        'rclone_args': 'Extra Args (One per line)',
        'rclone_args_ph': 'use_temp_mutime = false',
        'btn_save': 'Save',
        'btn_update': 'Update',
        'btn_sync_files': '🔄 Sync Config to Files',
        'list_title': 'Existing Nodes',
        'col_proto': 'Proto',
        'col_name': 'Name',
        'col_ip': 'Remote & Local Mappings',
        'remote_target': 'Remote',
        'local_path': 'Local Mount',
        'col_action': 'Actions',
        'btn_edit': 'Edit',
        'btn_delete': 'Delete',
        'confirm_del': 'Confirm delete?',
        'no_nodes': 'No nodes found.',
        'script_1_title': '1. startup.sh',
        'script_1_desc': 'It mounts remote nodes first, then starts the container.',
        'fuse_hint': '⚠️ <b>Rclone Mount Note</b>: When using Rclone on Linux (like Ubuntu), ensure <code>fuse3</code> or <code>fuse</code> is installed on the host.',
        'script_2_title': '2. shutdown.sh',
        'script_2_desc': 'It stops the container first, then unmounts paths safely.',
        'script_3_title': '3. docker-compose.yml',
        'btn_copy_script': 'Copy Script',
        'btn_copy_yaml': 'Copy YAML',
        'copied': '✅ Copied',
        'flash_sync_ok': '✅ Files and scripts synced successfully!',
        'flash_global_db_only': '✅ Global settings saved to DB! Please click "Sync Config to Files" to apply.',
        'flash_update_db_only': '✅ Node "{name}" saved to DB! Please click "Sync Config to Files" to apply.',
        'flash_add_ok': '✅ Node "{name}" added! (Files auto-synced)',
        'flash_name_err': '❌ Duplicate name "{name}".',
        'flash_del_db_only': '🗑️ Node removed from DB! Please click "Sync Config to Files" to apply.',
        'restore_card_title': 'Backrest Restore Guide',
        'restore_path': '/data/dest/custom_folder',
        'restore_p1': 'Specify target path when restoring:',
        'restore_p2': '⚠️ Folder must be empty or new.',
        'restore_p3': 'Files are stored in <code>backrest_data</code> volume.',
        'obscure_title': 'Rclone Password Obscuration Guide',
        'obscure_p1': 'To use Rclone connections like SFTP that require a password, run the following Docker command in your host terminal to generate an obscured password:',
        'obscure_cmd': "docker run --rm rclone/rclone:latest obscure 'your_real_password'",
        'obscure_p2': 'Copy the output (e.g., <code>v1M_...</code>) and paste it into the "Password" field.',
        
        # Script translation
        'sh_start_mount': '=== Starting Remote Mounts ===',
        'sh_proc_node': 'Processing node:',
        'sh_no_nodes': '(No nodes configured)',
        'sh_mount_done': 'Mount operations completed.',
        'sh_start_svc': '=== Starting Backrest Service ===',
        'sh_svc_done': 'Service started successfully!',
        'sh_stop_svc': '=== Stopping Backrest Service ===',
        'sh_start_umount': '=== Starting Remote Unmounts ===',
        'sh_proc_umount': 'Unmounting node:',
        'sh_no_umount': '(No nodes to unmount)',
        'sh_umount_done': 'Stop and unmount operations completed!'
    },
    'vi': {
        'title': 'Trung tâm Cấu hình Sao lưu',
        'tab_nodes': 'Quản lý Node Từ xa',
        'tab_scripts': 'Kịch bản Vận hành',
        'tab_restore': 'Hướng dẫn Khôi phục',
        'global_settings': 'Cài đặt Toàn cục (Global)',
        'ext_port': 'Port Ngoài:',
        'global_mount': 'Đường dẫn Mount:',
        'tz_label': 'Múi giờ (TZ):',
        'apply_global': 'Áp dụng',
        'hint_global': '💡 Sau khi sửa/xóa, hãy nhấp "Đồng bộ cấu hình ra tệp". Thêm mới sẽ tự động đồng bộ.',
        'add_node': 'Thêm Node',
        'cancel_edit': 'Hủy',
        'protocol': 'Giao thức',
        'node_name': 'Tên Định danh',
        'desc': 'Mô tả',
        'desc_ph': 'vd: Sao lưu SOP nhà máy Việt Nam',
        'ip': 'IP Máy chủ / Host',
        'port': 'Cổng (Port)',
        'remote_path': 'Đường dẫn Từ xa',
        'remote_path_ph': 'SharedFolder hoặc /volume1/data',
        'username': 'Tài khoản',
        'password': 'Mật khẩu',
        'rclone_pass_hint': '💡 Dùng rclone obscure để tạo mật khẩu SFTP',
        'rclone_type': 'Loại Rclone',
        'rclone_type_ph': 'vd: sftp, s3',
        'rclone_args': 'Tham số phụ (Mỗi dòng 1 tham số)',
        'rclone_args_ph': 'use_temp_mutime = false',
        'btn_save': 'Lưu Node',
        'btn_update': 'Cập nhật Node',
        'btn_sync_files': '🔄 Đồng bộ cấu hình ra tệp',
        'list_title': 'Danh sách Node',
        'col_proto': 'Giao thức',
        'col_name': 'Định danh',
        'col_ip': 'Ánh xạ Từ xa & Cục bộ',
        'remote_target': 'Từ xa',
        'local_path': 'Cục bộ',
        'col_action': 'Thao tác',
        'btn_edit': 'Sửa',
        'btn_delete': 'Xóa',
        'confirm_del': 'Bạn có chắc chắn muốn xóa?',
        'no_nodes': 'Chưa có kết nối nào.',
        'script_1_title': '1. startup.sh',
        'script_1_desc': 'Kịch bản sẽ mount các node trước, sau đó bật container Docker.',
        'fuse_hint': '⚠️ <b>Lưu ý Rclone</b>: Trên Linux (như Ubuntu), cần cài đặt gói <code>fuse3</code> hoặc <code>fuse</code>.',
        'script_2_title': '2. shutdown.sh',
        'script_2_desc': 'Nó sẽ dừng container trước, sau đó unmount an toàn.',
        'script_3_title': '3. docker-compose.yml',
        'btn_copy_script': 'Sao chép',
        'btn_copy_yaml': 'Sao chép YAML',
        'copied': '✅ Đã chép',
        'flash_sync_ok': '✅ Đã đồng bộ các tệp và kịch bản thành công!',
        'flash_global_db_only': '✅ Cài đặt đã lưu vào DB! Nhấp "Đồng bộ cấu hình ra tệp" để áp dụng.',
        'flash_update_db_only': '✅ Node "{name}" đã lưu! Nhấp "Đồng bộ cấu hình ra tệp" để áp dụng.',
        'flash_add_ok': '✅ Đã thêm node "{name}"! (Tự động đồng bộ tệp)',
        'flash_name_err': '❌ Lỗi: Tên "{name}" đã tồn tại.',
        'flash_del_db_only': '🗑️ Đã xóa node! Nhấp "Đồng bộ cấu hình ra tệp" để áp dụng.',
        'restore_card_title': 'Lưu ý khi Khôi phục',
        'restore_path': '/data/dest/ten_thu_muc',
        'restore_p1': 'Phải đặt đường dẫn đích thành:',
        'restore_p2': '⚠️ Thư mục này phải trống.',
        'restore_p3': 'Tệp nằm trên <code>backrest_data</code> volume.',
        'obscure_title': 'Hướng dẫn Tạo mật khẩu Rclone Obscure',
        'obscure_p1': 'Để sử dụng các kết nối Rclone như SFTP cần mật khẩu, hãy chạy lệnh Docker sau trong terminal của máy chủ để tạo mật khẩu mã hóa:',
        'obscure_cmd': "docker run --rm rclone/rclone:latest obscure 'mat_khau_that_cua_ban'",
        'obscure_p2': 'Sao chép chuỗi kết quả (ví dụ: <code>v1M_...</code>) và dán vào trường "Mật khẩu".',
        
        # Script translation
        'sh_start_mount': '=== Bắt đầu Mount Từ xa ===',
        'sh_proc_node': 'Đang xử lý node:',
        'sh_no_nodes': '(Không có node nào được cấu hình)',
        'sh_mount_done': 'Đã hoàn tất mount.',
        'sh_start_svc': '=== Khởi động Dịch vụ Backrest ===',
        'sh_svc_done': 'Khởi động dịch vụ thành công!',
        'sh_stop_svc': '=== Dừng Dịch vụ Backrest ===',
        'sh_start_umount': '=== Bắt đầu Unmount Từ xa ===',
        'sh_proc_umount': 'Đang unmount node:',
        'sh_no_umount': '(Không có node nào cần unmount)',
        'sh_umount_done': 'Đã hoàn tất dừng và unmount!'
    }
}

def get_locale():
    if has_request_context():
        return request.cookies.get('lang', 'zh')
    return 'zh'

# ==========================================
# 系統初始化與資料庫升級
# ==========================================
def init_system():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proto TEXT NOT NULL,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                server_ip TEXT,
                remote_path TEXT,
                username TEXT,
                password TEXT,
                rclone_type TEXT,
                rclone_args TEXT,
                port INTEGER
            )
        ''')
        try:
            conn.execute("ALTER TABLE servers ADD COLUMN port INTEGER")
            conn.execute("ALTER TABLE servers ADD COLUMN rclone_type TEXT")
            conn.execute("ALTER TABLE servers ADD COLUMN rclone_args TEXT")
        except sqlite3.OperationalError:
            pass

        conn.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('ext_port', '9898')")
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('global_host_mount', '/mnt/source')")
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('tz', '')")
    
    if not os.path.exists(RCLONE_FILE):
        open(RCLONE_FILE, 'a').close()
        
    sync_db_to_files('zh')

def sync_db_to_files(lang=None):
    if not lang:
        lang = get_locale()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['zh'])

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM servers").fetchall()
        ext_port = conn.execute("SELECT value FROM settings WHERE key='ext_port'").fetchone()['value']
        global_host_mount = conn.execute("SELECT value FROM settings WHERE key='global_host_mount'").fetchone()['value']
        tz = conn.execute("SELECT value FROM settings WHERE key='tz'").fetchone()
        tz_val = tz['value'] if tz else ""

    # 1. YAML (加入 profiles: ["manual"], restart: "no", 及 TZ 環境變數)
    if os.path.exists(COMPOSE_FILE):
        with open(COMPOSE_FILE, 'r', encoding='utf-8') as f: compose_data = yaml.load(f) or {}
    else: compose_data = {'version': '3.8', 'services': {}, 'volumes': {}}
    
    compose_data.setdefault('services', {})
    
    backrest_config = {
        'image': 'garethgeorge/backrest:latest',
        'container_name': 'backrest',
        'restart': 'no',  
        'profiles': ['manual'],
        'ports': [f"{ext_port}:9898"],
        'volumes': ['./backrest_config:/config', 'backrest_data:/data/dest', f"{global_host_mount}:/data/source:ro"]
    }
    
    if tz_val.strip():
        backrest_config['environment'] = [f"TZ={tz_val.strip()}"]

    compose_data['services']['backrest'] = backrest_config
    
    compose_data.setdefault('volumes', {})['backrest_data'] = None
    with open(COMPOSE_FILE, 'w', encoding='utf-8') as f: yaml.dump(compose_data, f)

    # 2. rclone.conf
    rclone_conf = []
    for r in rows:
        if r['proto'] == 'rclone':
            rclone_conf.append(f"[{r['name']}]")
            if r['rclone_type']: rclone_conf.append(f"type = {r['rclone_type']}")
            if r['server_ip']: rclone_conf.append(f"host = {r['server_ip']}")
            if r['port']: rclone_conf.append(f"port = {r['port']}")
            if r['username']: rclone_conf.append(f"user = {r['username']}")
            if r['password']: rclone_conf.append(f"pass = {r['password']}")
            if r['rclone_args']: 
                for line in r['rclone_args'].split('\n'):
                    if line.strip(): rclone_conf.append(line.strip())
            rclone_conf.append("")
    with open(RCLONE_FILE, 'w', encoding='utf-8') as f: f.write("\n".join(rclone_conf))

    # 3. Startup & Shutdown
    startup = ["#!/bin/bash", f'echo "{t["sh_start_mount"]}"']
    shutdown = ["#!/bin/bash", f'echo "{t["sh_stop_svc"]}"', "docker compose --profile manual down", f'echo "{t["sh_start_umount"]}"']
    
    has_nodes = False
    for r in rows:
        mount_point = f"{global_host_mount}/{r['name']}"
        if r['proto'] in ['smb', 'nfs', 'rclone']:
            has_nodes = True
            startup.append(f'echo "{t["sh_proc_node"]} {r["name"]} ({r["proto"].upper()})"')
            if r['proto'] == 'smb':
                startup.append(f"sudo mkdir -p {mount_point} && sudo mount -t cifs -o ro,username='{r['username']}',password='{r['password']}',iocharset=utf8,vers=3.0 //{(r['server_ip'] or '').strip()}/{(r['remote_path'] or '').lstrip('/')} {mount_point}")
            elif r['proto'] == 'nfs':
                startup.append(f"sudo mkdir -p {mount_point} && sudo mount -t nfs -o ro,nolock,noatime,tcp {(r['server_ip'] or '').strip()}:/{(r['remote_path'] or '').lstrip('/')} {mount_point}")
            elif r['proto'] == 'rclone':
                startup.append(f"sudo mkdir -p {mount_point} && sudo rclone mount {r['name']}:/{(r['remote_path'] or '').lstrip('/')} {mount_point} --config $(pwd)/rclone.conf --daemon --allow-other --read-only --vfs-cache-mode minimal")
            
            shutdown.append(f'echo "{t["sh_proc_umount"]} {r["name"]}"')
            shutdown.append(f"sudo umount {mount_point} || sudo fusermount -uz {mount_point}")

    if not has_nodes:
        startup.append(f'echo "{t["sh_no_nodes"]}"')
        shutdown.append(f'echo "{t["sh_no_umount"]}"')

    startup.extend([
        f'echo "{t["sh_mount_done"]}"\n',
        f'echo "{t["sh_start_svc"]}"',
        'docker compose --profile manual up -d',
        f'echo "{t["sh_svc_done"]}"'
    ])
    shutdown.append(f'echo "{t["sh_umount_done"]}"')

    with open(STARTUP_FILE, 'w') as f: f.write("\n".join(startup))
    with open(SHUTDOWN_FILE, 'w') as f: f.write("\n".join(shutdown))
    os.chmod(STARTUP_FILE, 0o755)
    os.chmod(SHUTDOWN_FILE, 0o755)

init_system()

# ==========================================
# 前端介面
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <title>{{ t.title }}</title>
    <style>
        :root { --bg: #f9f9f8; --card: #fff; --text: #333; --muted: #888; --border: #e5e5e5; --btn: #5c5c5c; --danger: #cc0000; --success: #6b8e23;}
        body { font-family: 'Helvetica Neue', Arial, sans-serif; background: var(--bg); color: var(--text); padding: 40px; margin: 0; display: flex; justify-content: center;}
        .container { width: 100%; max-width: 900px; position: relative; }
        .tabs { display: flex; border-bottom: 1px solid var(--border); margin-bottom: 20px; }
        .tab-btn { background: none; border: none; padding: 10px 20px; font-size: 1.05rem; cursor: pointer; color: var(--muted); border-bottom: 2px solid transparent; }
        .tab-btn.active { color: var(--text); border-bottom: 2px solid var(--text); font-weight: 500; }
        .tab-content { display: none; }
        .tab-content.active { display: block; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .card { background: var(--card); border: 1px solid var(--border); border-radius: 4px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);}
        .card h2 { margin-top: 0; font-size: 1.2rem; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 20px;}
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-size: 0.9rem; color: var(--muted); margin-bottom: 5px; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 3px; box-sizing: border-box; font-size: 1rem; color: var(--text);}
        input:focus, select:focus, textarea:focus { border-color: var(--btn); outline: none; }
        .btn { background: var(--btn); color: #fff; border: none; padding: 10px 20px; font-size: 1rem; border-radius: 3px; cursor: pointer; letter-spacing: 1px; transition: opacity 0.2s;}
        .btn:hover { opacity: 0.85; }
        .btn-small { padding: 5px 10px; font-size: 0.85rem; }
        .btn-danger { background: white; color: var(--danger); border: 1px solid var(--danger); }
        .alert { padding: 15px; margin-bottom: 20px; background: #f0f7e6; color: var(--success); border: 1px solid #d4e5c2; border-radius: 3px;}
        table { width: 100%; border-collapse: collapse; font-size: 0.95rem;}
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid var(--border); vertical-align: top; }
        .lang-selector { position: absolute; top: 0; right: 0; }
        .code-wrapper { position: relative; margin-top: 10px; }
        pre { background: #272822; color: #f8f8f2; padding: 20px; border-radius: 4px; overflow: auto; font-family: monospace; font-size: 0.9rem; margin:0;}
        .copy-btn { position: absolute; top: 8px; right: 8px; background: rgba(255,255,255,0.2); color: #fff; border: 1px solid rgba(255,255,255,0.4); padding: 4px 10px; font-size: 0.8rem; border-radius: 3px; cursor: pointer;}
        .copy-btn:hover { background: rgba(255,255,255,0.3); border-color: #fff; }
        .top-settings-bar { background: #f3f3f3; padding: 15px 20px; border-radius: 4px; margin-bottom: 20px; border: 1px solid var(--border); }
        .inline-form { display: flex; align-items: center; gap: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="lang-selector">
            <form action="/change_lang" method="POST" id="langForm" style="margin:0;">
                <select name="lang" onchange="document.cookie='lang='+this.value+'; path=/; max-age=31536000'; this.form.submit();">
                    <option value="zh" {% if lang=='zh' %}selected{% endif %}>🇹🇼 繁體中文</option>
                    <option value="en" {% if lang=='en' %}selected{% endif %}>🇺🇸 English</option>
                    <option value="vi" {% if lang=='vi' %}selected{% endif %}>🇻🇳 Tiếng Việt</option>
                </select>
            </form>
        </div>
        <h1 style="margin-bottom: 30px;">{{ t.title }}</h1>
        
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        
        <div class="tabs">
            <button class="tab-btn active" onclick="openTab('ConfigTab', this)">{{ t.tab_nodes }}</button>
            <button class="tab-btn" onclick="openTab('DocsTab', this)">{{ t.tab_scripts }}</button>
            <button class="tab-btn" onclick="openTab('RestoreTab', this)">{{ t.tab_restore }}</button>
        </div>

        <div id="ConfigTab" class="tab-content active">
            <div class="top-settings-bar">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h2 style="border:none; margin:0; font-size:1.1rem;">{{ t.global_settings }}</h2>
                    <form action="/sync_files" method="POST" style="margin:0;">
                        <button type="submit" class="btn" style="background: #4a6fa5;">{{ t.btn_sync_files }}</button>
                    </form>
                </div>
                <form action="/update_globals" method="POST" class="inline-form">
                    <label>{{ t.ext_port }} <input type="number" name="ext_port" value="{{ ext_port }}" style="width:80px; padding:6px; margin-left:5px;" required></label>
                    <label>{{ t.global_mount }} <input type="text" name="global_host_mount" value="{{ global_host_mount }}" style="width:160px; padding:6px; margin-left:5px;" required></label>
                    <label>{{ t.tz_label }} <input type="text" name="tz" value="{{ tz }}" style="width:120px; padding:6px; margin-left:5px;" placeholder="Asia/Taipei"></label>
                    <button type="submit" class="btn btn-small">{{ t.apply_global }}</button>
                </form>
                <div style="font-size: 0.85rem; color: var(--muted); margin-top: 10px;">{{ t.hint_global }}</div>
            </div>

            <div class="card" id="formCard">
                <div class="form-header">
                    <h2 id="formTitle">{{ t.add_node }}</h2>
                    <button type="button" class="btn btn-small" style="display:none;" id="btnCancelEdit" onclick="resetForm()">{{ t.cancel_edit }}</button>
                </div>
                <form action="/save" method="POST" id="configForm">
                    <input type="hidden" name="id" id="f_id">
                    
                    <div class="grid">
                        <div class="form-group">
                            <label>{{ t.protocol }}</label>
                            <select name="proto" id="f_proto" onchange="toggleUI()" required>
                                <option value="smb">SMB / CIFS</option>
                                <option value="nfs">NFS</option>
                                <option value="rclone">Rclone (Cloud/SFTP)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>{{ t.node_name }}</label>
                            <input type="text" name="name" id="f_name" required>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>{{ t.desc }}</label>
                        <input type="text" name="description" id="f_desc" placeholder="{{ t.desc_ph }}" required>
                    </div>

                    <div class="grid">
                        <div class="form-group" id="wrap_ip">
                            <label>{{ t.ip }}</label>
                            <input type="text" name="server_ip" id="f_ip">
                        </div>
                        <div class="form-group">
                            <label>{{ t.port }}</label>
                            <input type="number" name="port" id="f_port" placeholder="22, 445, etc.">
                        </div>
                    </div>
                    <div class="form-group">
                        <label>{{ t.remote_path }}</label>
                        <input type="text" name="remote_path" id="f_path" placeholder="{{ t.remote_path_ph }}">
                    </div>

                    <div class="grid" id="wrap_auth">
                        <div class="form-group">
                            <label>{{ t.username }}</label>
                            <input type="text" name="username" id="f_user">
                        </div>
                        <div class="form-group">
                            <label>{{ t.password }}</label>
                            <input type="password" name="password" id="f_pass">
                            <small style="color:var(--muted); display:none; margin-top:5px;" id="rclone_pass_hint">{{ t.rclone_pass_hint }}</small>
                        </div>
                    </div>

                    <div id="wrap_rclone" style="display:none;">
                        <div class="form-group">
                            <label>{{ t.rclone_type }}</label>
                            <input type="text" name="rclone_type" id="f_rtype" placeholder="{{ t.rclone_type_ph }}">
                        </div>
                        <div class="form-group">
                            <label>{{ t.rclone_args }}</label>
                            <textarea name="rclone_args" id="f_rargs" rows="2" placeholder="{{ t.rclone_args_ph }}"></textarea>
                        </div>
                    </div>

                    <div style="margin-top: 10px;">
                        <button type="submit" class="btn" id="btnSubmit">{{ t.btn_save }}</button>
                        <button type="button" class="btn" style="background:#eee; color:#333; display:none; margin-left:10px;" id="btnCancel" onclick="resetForm()">{{ t.cancel_edit }}</button>
                    </div>
                </form>
            </div>

            <div class="card">
                <h2>{{ t.list_title }}</h2>
                <table>
                    <thead><tr><th>{{ t.col_proto }}</th><th>{{ t.col_name }}</th><th>{{ t.col_ip }}</th><th style="width: 120px;">{{ t.col_action }}</th></tr></thead>
                    <tbody>
                        {% for item in servers %}
                        <tr>
                            <td><span style="background:#eee; padding:3px 8px; border-radius:12px; font-size:0.8rem; text-transform:uppercase;">{{ item.proto }}</span></td>
                            <td><strong>{{ item.name }}</strong><br><small style="color:var(--muted);">{{ item.description }}</small></td>
                            <td>
                                <div style="margin-bottom: 4px;"><span style="color:var(--muted); font-size:0.8rem;">{{ t.remote_target }}:</span> {{ item.server_ip or '-' }}{% if item.port %}:{{ item.port }}{% endif %}/{{ item.remote_path }}</div>
                                <div><span style="color:var(--muted); font-size:0.8rem;">{{ t.local_path }}:</span> {{ global_host_mount }}/{{ item.name }}</div>
                            </td>
                            <td>
                                <button class="btn" style="padding:4px 8px; font-size:0.8rem;" onclick='edit({{ item | tojson | safe }})'>{{ t.btn_edit }}</button>
                                <form action="/delete/{{ item.id }}" method="POST" onsubmit="return confirm('{{ t.confirm_del }}');" style="display:inline;">
                                    <button type="submit" class="btn btn-danger" style="padding:4px 8px; font-size:0.8rem;">{{ t.btn_delete }}</button>
                                </form>
                            </td>
                        </tr>
                        {% else %}
                        <tr><td colspan="4" style="text-align:center; color:var(--muted);">{{ t.no_nodes }}</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div id="DocsTab" class="tab-content">
            <div class="card">
                <h2>{{ t.script_1_title }}</h2>
                <p>{{ t.script_1_desc }}</p>
                <p style="color: var(--muted); font-size: 0.9rem;">{{ t.fuse_hint | safe }}</p>
                <div class="code-wrapper"><button class="copy-btn" onclick="copyCode(this, 'code-startup')">{{ t.btn_copy_script }}</button><pre id="code-startup">{{ startup_content }}</pre></div>
            </div>
            <div class="card">
                <h2>{{ t.script_2_title }}</h2>
                <p>{{ t.script_2_desc }}</p>
                <div class="code-wrapper"><button class="copy-btn" onclick="copyCode(this, 'code-shutdown')">{{ t.btn_copy_script }}</button><pre id="code-shutdown">{{ shutdown_content }}</pre></div>
            </div>
            <div class="card">
                <h2>{{ t.script_3_title }}</h2>
                <div class="code-wrapper"><button class="copy-btn" onclick="copyCode(this, 'code-yaml')">{{ t.btn_copy_yaml }}</button><pre id="code-yaml">{{ compose_content }}</pre></div>
            </div>
        </div>

        <div id="RestoreTab" class="tab-content">
            <div class="card" style="line-height: 1.6;">
                <h2>{{ t.restore_card_title }}</h2>
                <p>{{ t.restore_p1 }}</p>
                <div class="code-wrapper"><pre style="color: #a6e22e; font-weight: bold; font-size: 1.05rem;">{{ t.restore_path }}</pre></div>
                <p style="margin-top: 15px;">{{ t.restore_p2 | safe }}</p>
                <p>{{ t.restore_p3 | safe }}</p>
            </div>
            
            <div class="card" style="line-height: 1.6;">
                <h2>{{ t.obscure_title }}</h2>
                <p>{{ t.obscure_p1 }}</p>
                <div class="code-wrapper">
                    <button class="copy-btn" onclick="copyCode(this, 'code-obscure')">{{ t.btn_copy_script }}</button>
                    <pre id="code-obscure">{{ t.obscure_cmd }}</pre>
                </div>
                <p style="margin-top: 15px;">{{ t.obscure_p2 | safe }}</p>
            </div>
        </div>
    </div>

    <script>
        function openTab(name, btn) {
            document.querySelectorAll('.tab-content').forEach(d => d.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            btn.classList.add('active');
        }

        function toggleUI() {
            const p = document.getElementById('f_proto').value;
            const wAuth = document.getElementById('wrap_auth');
            const wRclone = document.getElementById('wrap_rclone');
            const hintPass = document.getElementById('rclone_pass_hint');
            
            ['f_ip', 'f_path', 'f_user', 'f_pass', 'f_rtype'].forEach(id => document.getElementById(id).required = false);

            if (p === 'smb') {
                wAuth.style.display = 'grid';
                wRclone.style.display = 'none';
                hintPass.style.display = 'none';
                document.getElementById('f_ip').required = true;
                document.getElementById('f_path').required = true;
                document.getElementById('f_user').required = true;
                document.getElementById('f_pass').required = true;
            } else if (p === 'nfs') {
                wAuth.style.display = 'none';
                wRclone.style.display = 'none';
                hintPass.style.display = 'none';
                document.getElementById('f_ip').required = true;
                document.getElementById('f_path').required = true;
            } else if (p === 'rclone') {
                wAuth.style.display = 'grid'; 
                wRclone.style.display = 'block';
                hintPass.style.display = 'block';
                document.getElementById('f_rtype').required = true;
            }
        }

        function edit(d) {
            document.getElementById('f_id').value = d.id;
            document.getElementById('f_proto').value = d.proto;
            document.getElementById('f_name').value = d.name;
            document.getElementById('f_desc').value = d.description;
            document.getElementById('f_ip').value = d.server_ip || '';
            document.getElementById('f_port').value = d.port || '';
            document.getElementById('f_path').value = d.remote_path || '';
            document.getElementById('f_user').value = d.username || '';
            document.getElementById('f_pass').value = d.password || '';
            document.getElementById('f_rtype').value = d.rclone_type || '';
            document.getElementById('f_rargs').value = d.rclone_args || '';
            
            toggleUI();
            
            document.getElementById('formTitle').innerText = '{{ t.btn_edit }}：' + d.name;
            document.getElementById('btnSubmit').innerText = '{{ t.btn_update }}';
            document.getElementById('btnCancel').style.display = 'inline-block';
            window.scrollTo(0,0);
        }

        function resetForm() {
            document.getElementById('configForm').reset();
            document.getElementById('f_id').value = '';
            document.getElementById('formTitle').innerText = '{{ t.add_node }}';
            document.getElementById('btnSubmit').innerText = '{{ t.btn_save }}';
            document.getElementById('btnCancel').style.display = 'none';
            toggleUI();
        }

        function copyCode(btn, id) {
            const text = document.getElementById(id).innerText;
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(text).then(()=>success(btn)).catch(()=>fallback(text, btn));
            } else { fallback(text, btn); }
        }
        function success(btn) {
            const org = btn.innerText; btn.innerText = '{{ t.copied }}';
            btn.style.background = 'var(--success)'; btn.style.borderColor = 'var(--success)';
            setTimeout(() => { btn.innerText = org; btn.style.background = ''; btn.style.borderColor = ''; }, 2000);
        }
        function fallback(text, btn) {
            const ta = document.createElement("textarea"); ta.value = text;
            ta.style.position="fixed"; ta.style.opacity="0"; document.body.appendChild(ta);
            ta.select(); document.execCommand('copy'); ta.remove(); success(btn);
        }

        toggleUI();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    lang = get_locale(); t = TRANSLATIONS.get(lang, TRANSLATIONS['zh'])
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        servers = [dict(r) for r in conn.execute("SELECT * FROM servers ORDER BY id DESC")]
        ext_port = conn.execute("SELECT value FROM settings WHERE key='ext_port'").fetchone()['value']
        global_mount = conn.execute("SELECT value FROM settings WHERE key='global_host_mount'").fetchone()['value']
        tz_setting = conn.execute("SELECT value FROM settings WHERE key='tz'").fetchone()
        tz_val = tz_setting['value'] if tz_setting else ""
    
    def read_f(p): return open(p).read() if os.path.exists(p) else ""
    return render_template_string(HTML_TEMPLATE, servers=servers, lang=lang, t=t, 
                                  ext_port=ext_port, global_host_mount=global_mount, tz=tz_val,
                                  startup_content=read_f(STARTUP_FILE), 
                                  shutdown_content=read_f(SHUTDOWN_FILE),
                                  compose_content=read_f(COMPOSE_FILE))

@app.route('/change_lang', methods=['POST'])
def change_lang():
    # 僅作頁面跳轉，因為 Cookie 已經由前端 JavaScript 寫入
    # 此動作不再觸發 sync_db_to_files()，避免意外覆寫實體檔案
    return redirect('/')

@app.route('/sync_files', methods=['POST'])
def sync_files():
    t = TRANSLATIONS.get(get_locale(), TRANSLATIONS['zh'])
    sync_db_to_files()
    flash(t['flash_sync_ok'])
    return redirect('/')

@app.route('/update_globals', methods=['POST'])
def update_globals():
    t = TRANSLATIONS.get(get_locale(), TRANSLATIONS['zh'])
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE settings SET value=? WHERE key='ext_port'", (request.form.get('ext_port'),))
        conn.execute("UPDATE settings SET value=? WHERE key='global_host_mount'", (request.form.get('global_host_mount').rstrip('/'),))
        conn.execute("UPDATE settings SET value=? WHERE key='tz'", (request.form.get('tz', '').strip(),))
    
    # 僅寫入資料庫，不自動更新檔案
    flash(t['flash_global_db_only'])
    return redirect('/')

@app.route('/save', methods=['POST'])
def save():
    t = TRANSLATIONS.get(get_locale(), TRANSLATIONS['zh'])
    port_val = request.form.get('port')
    
    data = {
        'id': request.form.get('id'), 'proto': request.form.get('proto'),
        'name': request.form.get('name').strip(), 'description': request.form.get('description'),
        'server_ip': request.form.get('server_ip', ''), 'remote_path': request.form.get('remote_path', ''),
        'username': request.form.get('username', ''), 'password': request.form.get('password', ''),
        'rclone_type': request.form.get('rclone_type', ''), 'rclone_args': request.form.get('rclone_args', ''),
        'port': int(port_val) if port_val and port_val.isdigit() else 0
    }
    
    with sqlite3.connect(DB_PATH) as conn:
        try:
            if data['id']:
                conn.execute("UPDATE servers SET proto=:proto, name=:name, description=:description, server_ip=:server_ip, remote_path=:remote_path, username=:username, password=:password, rclone_type=:rclone_type, rclone_args=:rclone_args, port=:port WHERE id=:id", data)
                flash(t['flash_update_db_only'].format(name=data['name']))
            else:
                conn.execute("INSERT INTO servers (proto, name, description, server_ip, remote_path, username, password, rclone_type, rclone_args, port) VALUES (:proto, :name, :description, :server_ip, :remote_path, :username, :password, :rclone_type, :rclone_args, :port)", data)
                # 新增節點時，自動觸發同步更新實體檔案
                sync_db_to_files()
                flash(t['flash_add_ok'].format(name=data['name']))
        except sqlite3.IntegrityError:
            flash(t['flash_name_err'].format(name=data['name']), 'error')
            
    return redirect('/')

@app.route('/delete/<int:record_id>', methods=['POST'])
def delete(record_id):
    t = TRANSLATIONS.get(get_locale(), TRANSLATIONS['zh'])
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM servers WHERE id=?", (record_id,))
        
    # 僅寫入資料庫，不自動更新檔案
    flash(t['flash_del_db_only'])
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)