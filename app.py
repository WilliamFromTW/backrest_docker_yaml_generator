import os
import sqlite3
from flask import Flask, render_template_string, request, flash, redirect, url_for, has_request_context
from ruamel.yaml import YAML

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_rclone_fields'

CONFIG_DIR = docker-compose
DB_PATH = os.path.join(CONFIG_DIR, configs.db)
COMPOSE_FILE = os.path.join(CONFIG_DIR, docker-compose.yml)
STARTUP_FILE = os.path.join(CONFIG_DIR, startup.sh)
SHUTDOWN_FILE = os.path.join(CONFIG_DIR, shutdown.sh)
RCLONE_FILE = os.path.join(CONFIG_DIR, rclone.conf)

yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)

# ==========================================
# 多國語系字典檔 (i18n)
# ==========================================
TRANSLATIONS = {
    'zh' {
        'title' '備份組態管理中樞',
        'tab_nodes' '遠端節點管理',
        'tab_scripts' '維運腳本 (啟動停用)',
        'tab_restore' '還原說明 (Restore)',
        'global_settings' '系統全域設定 (Global Settings)',
        'ext_port' '外部 Port',
        'global_mount' '宿主機全域掛載根目錄',
        'apply_global' '套用全域設定',
        'hint_global' '💡 提示：若新增掛載點，系統將自動更新 docker-compose 目錄下的 startup.sh 與 shutdown.sh。',
        'add_node' '新增遠端連線節點',
        'cancel_edit' '取消編輯',
        'protocol' '通訊協定 (Protocol)',
        'node_name' '連線識別名稱 (作為目錄名)',
        'desc' '用途說明',
        'desc_ph' '例如：越南廠 SOP 圖檔每日備份',
        'ip' '伺服器 IP  Host',
        'port' '通訊埠 (Port)',
        'remote_path' '遠端路徑 (Remote Path)',
        'remote_path_ph' 'SharedFolder 或 volume1data',
        'username' '帳號 (Username)',
        'password' '密碼 (Password  Obscured)',
        'rclone_pass_hint' '💡 若為 Rclone SFTP，請填入 rclone obscure 加密後的密碼',
        'rclone_type' 'Rclone 類型 (type)',
        'rclone_type_ph' '例如 sftp, s3, drive',
        'rclone_args' 'Rclone 額外參數 (每行一個)',
        'rclone_args_ph' 'pubkey_file = pathtokeynuse_temp_mutime = false',
        'btn_save' '儲存節點資訊',
        'btn_update' '更新節點資訊',
        'list_title' '現有連線節點清單',
        'col_proto' '協定',
        'col_name' '識別名稱',
        'col_ip' '遠端與本地掛載對應',
        'remote_target' '遠端來源',
        'local_path' '本地掛載點',
        'col_action' '操作',
        'btn_edit' '編輯',
        'btn_delete' '刪除',
        'confirm_del' '確定要刪除此節點嗎？',
        'no_nodes' '目前尚無任何連線設定。',
        'script_1_title' '1. 啟動腳本 (startup.sh)',
        'script_1_desc' '系統已自動在 docker-compose 目錄下產生 startup.sh 並賦予執行權限。此腳本會先進行掛載，隨後才啟動 Docker 容器。',
        'fuse_hint' '⚠️ bRclone 掛載提醒b：在 Linux (如 Ubuntu) 環境使用 Rclone 掛載時，宿主機需預先安裝 codefuse3code 或 codefusecode 相關套件 (例如執行：codesudo apt install fuse3code)。',
        'script_2_title' '2. 停用與卸載腳本 (shutdown.sh)',
        'script_2_desc' '系統已自動在 docker-compose 目錄下產生 shutdown.sh 並賦予執行權限。此腳本會先停用 Docker 容器，再安全地卸載所有路徑。',
        'script_3_title' '3. docker-compose.yml',
        'btn_copy_script' '複製腳本',
        'btn_copy_yaml' '複製 YAML',
        'copied' '✅ 已複製',
        'flash_global_ok' '✅ 全域設定已更新！',
        'flash_update_ok' '✅ 節點「{name}」已更新！',
        'flash_add_ok' '✅ 成功新增節點「{name}」！',
        'flash_name_err' '❌ 名稱「{name}」重複。',
        'flash_del_ok' '🗑️ 節點已移除。',
        'restore_card_title' 'Backrest 快照還原注意事項',
        'restore_path' 'datadest自訂目錄名稱',
        'restore_p1' '還原時請務必指定目標目錄：',
        'restore_p2' '⚠️ 目錄必須為空，否則還原會失敗。',
        'restore_p3' '還原後檔案位於宿主機 Volume codebackrest_datacode。',
        'obscure_title' 'Rclone 密碼加密教學 (Obscure)',
        'obscure_p1' '若要使用 SFTP 等需要密碼的 Rclone 連線，請在宿主機終端機執行以下 Docker 指令產生加密密碼：',
        'obscure_cmd' docker run --rm rclonerclonelatest obscure '您的真實密碼',
        'obscure_p2' '將終端機回傳的亂碼（例如 codev1M_...code）複製後，填入本系統的「密碼」欄位即可。',
        
        # 腳本內部翻譯
        'sh_start_mount' '=== 開始掛載遠端資料來源 ===',
        'sh_proc_node' '正在處理節點：',
        'sh_no_nodes' '(目前沒有設定任何節點)',
        'sh_mount_done' '掛載作業完成。',
        'sh_start_svc' '=== 啟動 Backrest 服務 ===',
        'sh_svc_done' '服務已啟動完畢！',
        'sh_stop_svc' '=== 停用 Backrest 服務 ===',
        'sh_start_umount' '=== 開始卸載遠端資料來源 ===',
        'sh_proc_umount' '正在卸載節點：',
        'sh_no_umount' '(目前沒有需要卸載的節點)',
        'sh_umount_done' '停用與卸載作業已全部完成！'
    },
    'en' {
        'title' 'Backup Config Hub',
        'tab_nodes' 'Remote Nodes',
        'tab_scripts' 'Ops Scripts',
        'tab_restore' 'Restore Guide',
        'global_settings' 'Global Settings',
        'ext_port' 'Ext Port',
        'global_mount' 'Host Mount Root',
        'apply_global' 'Apply',
        'hint_global' '💡 Hint System auto-updates scripts in the docker-compose folder.',
        'add_node' 'Add Node',
        'cancel_edit' 'Cancel',
        'protocol' 'Protocol',
        'node_name' 'Identifier',
        'desc' 'Description',
        'desc_ph' 'e.g., Vietnam factory SOP daily backup',
        'ip' 'Host  IP',
        'port' 'Port',
        'remote_path' 'Remote Path',
        'remote_path_ph' 'SharedFolder or volume1data',
        'username' 'Username',
        'password' 'Password  Obscured',
        'rclone_pass_hint' '💡 For Rclone SFTP, use rclone obscure for password',
        'rclone_type' 'Rclone Type',
        'rclone_type_ph' 'e.g., sftp, s3',
        'rclone_args' 'Extra Args (One per line)',
        'rclone_args_ph' 'use_temp_mutime = false',
        'btn_save' 'Save',
        'btn_update' 'Update',
        'list_title' 'Existing Nodes',
        'col_proto' 'Proto',
        'col_name' 'Name',
        'col_ip' 'Remote & Local Mappings',
        'remote_target' 'Remote',
        'local_path' 'Local Mount',
        'col_action' 'Actions',
        'btn_edit' 'Edit',
        'btn_delete' 'Delete',
        'confirm_del' 'Confirm delete',
        'no_nodes' 'No nodes found.',
        'script_1_title' '1. startup.sh',
        'script_1_desc' 'The system has auto-generated startup.sh with executable permissions. It mounts remote nodes first, then starts the container.',
        'fuse_hint' '⚠️ bRclone Mount Noteb When using Rclone on Linux (like Ubuntu), ensure codefuse3code or codefusecode is installed on the host (e.g., run codesudo apt install fuse3code).',
        'script_2_title' '2. shutdown.sh',
        'script_2_desc' 'The system has auto-generated shutdown.sh with executable permissions. It stops the container first, then unmounts paths safely.',
        'script_3_title' '3. docker-compose.yml',
        'btn_copy_script' 'Copy Script',
        'btn_copy_yaml' 'Copy YAML',
        'copied' '✅ Copied',
        'flash_global_ok' '✅ Global settings updated!',
        'flash_update_ok' '✅ Node {name} updated!',
        'flash_add_ok' '✅ Node {name} added!',
        'flash_name_err' '❌ Duplicate name {name}.',
        'flash_del_ok' '🗑️ Node removed.',
        'restore_card_title' 'Backrest Restore Guide',
        'restore_path' 'datadestcustom_folder',
        'restore_p1' 'Specify target path when restoring',
        'restore_p2' '⚠️ Folder must be empty or new.',
        'restore_p3' 'Files are stored in codebackrest_datacode volume.',
        'obscure_title' 'Rclone Password Obscuration Guide',
        'obscure_p1' 'To use Rclone connections like SFTP that require a password, run the following Docker command in your host terminal to generate an obscured password',
        'obscure_cmd' docker run --rm rclonerclonelatest obscure 'your_real_password',
        'obscure_p2' 'Copy the output (e.g., codev1M_...code) and paste it into the Password field.',
        
        # Script translation
        'sh_start_mount' '=== Starting Remote Mounts ===',
        'sh_proc_node' 'Processing node',
        'sh_no_nodes' '(No nodes configured)',
        'sh_mount_done' 'Mount operations completed.',
        'sh_start_svc' '=== Starting Backrest Service ===',
        'sh_svc_done' 'Service started successfully!',
        'sh_stop_svc' '=== Stopping Backrest Service ===',
        'sh_start_umount' '=== Starting Remote Unmounts ===',
        'sh_proc_umount' 'Unmounting node',
        'sh_no_umount' '(No nodes to unmount)',
        'sh_umount_done' 'Stop and unmount operations completed!'
    },
    'vi' {
        'title' 'Trung tâm Cấu hình Sao lưu',
        'tab_nodes' 'Quản lý Node Từ xa',
        'tab_scripts' 'Kịch bản Vận hành',
        'tab_restore' 'Hướng dẫn Khôi phục',
        'global_settings' 'Cài đặt Toàn cục (Global)',
        'ext_port' 'Port Ngoài',
        'global_mount' 'Đường dẫn Mount',
        'apply_global' 'Áp dụng',
        'hint_global' '💡 Hệ thống tự động cập nhật thư mục docker-compose.',
        'add_node' 'Thêm Node',
        'cancel_edit' 'Hủy',
        'protocol' 'Giao thức',
        'node_name' 'Tên Định danh',
        'desc' 'Mô tả',
        'desc_ph' 'vd Sao lưu SOP nhà máy Việt Nam',
        'ip' 'IP Máy chủ  Host',
        'port' 'Cổng (Port)',
        'remote_path' 'Đường dẫn Từ xa',
        'remote_path_ph' 'SharedFolder hoặc volume1data',
        'username' 'Tài khoản',
        'password' 'Mật khẩu',
        'rclone_pass_hint' '💡 Dùng rclone obscure để tạo mật khẩu SFTP',
        'rclone_type' 'Loại Rclone',
        'rclone_type_ph' 'vd sftp, s3',
        'rclone_args' 'Tham số phụ (Mỗi dòng 1 tham số)',
        'rclone_args_ph' 'use_temp_mutime = false',
        'btn_save' 'Lưu Node',
        'btn_update' 'Cập nhật Node',
        'list_title' 'Danh sách Node',
        'col_proto' 'Giao thức',
        'col_name' 'Định danh',
        'col_ip' 'Ánh xạ Từ xa & Cục bộ',
        'remote_target' 'Từ xa',
        'local_path' 'Cục bộ',
        'col_action' 'Thao tác',
        'btn_edit' 'Sửa',
        'btn_delete' 'Xóa',
        'confirm_del' 'Bạn có chắc chắn muốn xóa',
        'no_nodes' 'Chưa có kết nối nào.',
        'script_1_title' '1. startup.sh',
        'script_1_desc' 'Hệ thống đã tự động tạo startup.sh với quyền thực thi. Kịch bản sẽ mount các node trước, sau đó bật container Docker.',
        'fuse_hint' '⚠️ bLưu ý Rcloneb Trên Linux (như Ubuntu), cần cài đặt gói codefuse3code hoặc codefusecode trên máy chủ (ví dụ chạy codesudo apt install fuse3code).',
        'script_2_title' '2. shutdown.sh',
        'script_2_desc' 'Hệ thống đã tự động tạo shutdown.sh với quyền thực thi. Nó sẽ dừng container trước, sau đó unmount an toàn.',
        'script_3_title' '3. docker-compose.yml',
        'btn_copy_script' 'Sao chép',
        'btn_copy_yaml' 'Sao chép YAML',
        'copied' '✅ Đã chép',
        'flash_global_ok' '✅ Đã cập nhật cài đặt!',
        'flash_update_ok' '✅ Đã cập nhật node {name}!',
        'flash_add_ok' '✅ Đã thêm node {name}!',
        'flash_name_err' '❌ Lỗi Tên {name} đã tồn tại.',
        'flash_del_ok' '🗑️ Đã xóa node.',
        'restore_card_title' 'Lưu ý khi Khôi phục',
        'restore_path' 'datadestten_thu_muc',
        'restore_p1' 'Phải đặt đường dẫn đích thành',
        'restore_p2' '⚠️ Thư mục này phải trống.',
        'restore_p3' 'Tệp nằm trên codebackrest_datacode volume.',
        'obscure_title' 'Hướng dẫn Tạo mật khẩu Rclone Obscure',
        'obscure_p1' 'Để sử dụng các kết nối Rclone như SFTP cần mật khẩu, hãy chạy lệnh Docker sau trong terminal của máy chủ để tạo mật khẩu mã hóa',
        'obscure_cmd' docker run --rm rclonerclonelatest obscure 'mat_khau_that_cua_ban',
        'obscure_p2' 'Sao chép chuỗi kết quả (ví dụ codev1M_...code) và dán vào trường Mật khẩu.',
        
        # Script translation
        'sh_start_mount' '=== Bắt đầu Mount Từ xa ===',
        'sh_proc_node' 'Đang xử lý node',
        'sh_no_nodes' '(Không có node nào được cấu hình)',
        'sh_mount_done' 'Đã hoàn tất mount.',
        'sh_start_svc' '=== Khởi động Dịch vụ Backrest ===',
        'sh_svc_done' 'Khởi động dịch vụ thành công!',
        'sh_stop_svc' '=== Dừng Dịch vụ Backrest ===',
        'sh_start_umount' '=== Bắt đầu Unmount Từ xa ===',
        'sh_proc_umount' 'Đang unmount node',
        'sh_no_umount' '(Không có node nào cần unmount)',
        'sh_umount_done' 'Đã hoàn tất dừng và unmount!'
    }
}

def get_locale()
    if has_request_context()
        return request.cookies.get('lang', 'zh')
    return 'zh'

# ==========================================
# 系統初始化與資料庫升級
# ==========================================
def init_system()
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn
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
        try
            conn.execute(ALTER TABLE servers ADD COLUMN port INTEGER)
            conn.execute(ALTER TABLE servers ADD COLUMN rclone_type TEXT)
            conn.execute(ALTER TABLE servers ADD COLUMN rclone_args TEXT)
        except sqlite3.OperationalError
            pass

        conn.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
        conn.execute(INSERT OR IGNORE INTO settings (key, value) VALUES ('ext_port', '9898'))
        conn.execute(INSERT OR IGNORE INTO settings (key, value) VALUES ('global_host_mount', 'mntsource'))
    
    if not os.path.exists(RCLONE_FILE)
        open(RCLONE_FILE, 'a').close()
        
    sync_db_to_files('zh')

def sync_db_to_files(lang=None)
    if not lang
        lang = get_locale()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['zh'])

    with sqlite3.connect(DB_PATH) as conn
        conn.row_factory = sqlite3.Row
        rows = conn.execute(SELECT  FROM servers).fetchall()
        ext_port = conn.execute(SELECT value FROM settings WHERE key='ext_port').fetchone()['value']
        global_host_mount = conn.execute(SELECT value FROM settings WHERE key='global_host_mount').fetchone()['value']

    # 1. YAML (加入 profiles [manual])
    if os.path.exists(COMPOSE_FILE)
        with open(COMPOSE_FILE, 'r', encoding='utf-8') as f compose_data = yaml.load(f) or {}
    else compose_data = {'version' '3.8', 'services' {}, 'volumes' {}}
    
    compose_data.setdefault('services', {})
    compose_data['services']['backrest'] = {
        'image' 'garethgeorgebackrestlatest',
        'container_name' 'backrest',
        'restart' 'no',
        'profiles' ['manual'],  # 預設不隨伺服器啟動，必須透過 --profile manual 啟動
        'ports' [f{ext_port}9898],
        'volumes' ['.backrest_configconfig', 'backrest_datadatadest', f{global_host_mount}datasourcero]
    }
    compose_data.setdefault('volumes', {})['backrest_data'] = None
    with open(COMPOSE_FILE, 'w', encoding='utf-8') as f yaml.dump(compose_data, f)

    # 2. rclone.conf
    rclone_conf = []
    for r in rows
        if r['proto'] == 'rclone'
            rclone_conf.append(f[{r['name']}])
            if r['rclone_type'] rclone_conf.append(ftype = {r['rclone_type']})
            if r['server_ip'] rclone_conf.append(fhost = {r['server_ip']})
            if r['port'] rclone_conf.append(fport = {r['port']})
            if r['username'] rclone_conf.append(fuser = {r['username']})
            if r['password'] rclone_conf.append(fpass = {r['password']})
            if r['rclone_args'] 
                for line in r['rclone_args'].split('n')
                    if line.strip() rclone_conf.append(line.strip())
            rclone_conf.append()
    with open(RCLONE_FILE, 'w', encoding='utf-8') as f f.write(n.join(rclone_conf))

    # 3. Startup & Shutdown (使用 --profile manual 啟動並帶上語系翻譯)
    startup = [#!binbash, f'echo {t[sh_start_mount]}']
    shutdown = [#!binbash, f'echo {t[sh_stop_svc]}', docker compose --profile manual down, f'echo {t[sh_start_umount]}']
    
    has_nodes = False
    for r in rows
        mount_point = f{global_host_mount}{r['name']}
        if r['proto'] in ['smb', 'nfs', 'rclone']
            has_nodes = True
            startup.append(f'echo {t[sh_proc_node]} {r[name]} ({r[proto].upper()})')
            if r['proto'] == 'smb'
                startup.append(fsudo mkdir -p {mount_point} && sudo mount -t cifs -o ro,username='{r['username']}',password='{r['password']}',iocharset=utf8,vers=3.0 {(r['server_ip'] or '').strip()}{(r['remote_path'] or '').lstrip('')} {mount_point})
            elif r['proto'] == 'nfs'
                startup.append(fsudo mkdir -p {mount_point} && sudo mount -t nfs -o ro,nolock,noatime,tcp {(r['server_ip'] or '').strip()}{(r['remote_path'] or '').lstrip('')} {mount_point})
            elif r['proto'] == 'rclone'
                startup.append(fsudo mkdir -p {mount_point} && sudo rclone mount {r['name']}{(r['remote_path'] or '').lstrip('')} {mount_point} --config $(pwd)rclone.conf --daemon --allow-other --read-only --vfs-cache-mode minimal)
            
            shutdown.append(f'echo {t[sh_proc_umount]} {r[name]}')
            shutdown.append(fsudo umount {mount_point}  sudo fusermount -uz {mount_point})

    if not has_nodes
        startup.append(f'echo {t[sh_no_nodes]}')
        shutdown.append(f'echo {t[sh_no_umount]}')

    startup.extend([
        f'echo {t[sh_mount_done]}n',
        f'echo {t[sh_start_svc]}',
        'docker compose --profile manual up -d',
        f'echo {t[sh_svc_done]}'
    ])
    shutdown.append(f'echo {t[sh_umount_done]}')

    with open(STARTUP_FILE, 'w') as f f.write(n.join(startup))
    with open(SHUTDOWN_FILE, 'w') as f f.write(n.join(shutdown))
    os.chmod(STARTUP_FILE, 0o755)
    os.chmod(SHUTDOWN_FILE, 0o755)

init_system()

# ==========================================
# 前端介面
# ==========================================
HTML_TEMPLATE = 
!DOCTYPE html
html lang={{ lang }}
head
    meta charset=UTF-8
    title{{ t.title }}title
    style
        root { --bg #f9f9f8; --card #fff; --text #333; --muted #888; --border #e5e5e5; --btn #5c5c5c; --danger #cc0000; --success #6b8e23;}
        body { font-family 'Helvetica Neue', Arial, sans-serif; background var(--bg); color var(--text); padding 40px; margin 0; display flex; justify-content center;}
        .container { width 100%; max-width 900px; position relative; }
        .tabs { display flex; border-bottom 1px solid var(--border); margin-bottom 20px; }
        .tab-btn { background none; border none; padding 10px 20px; font-size 1.05rem; cursor pointer; color var(--muted); border-bottom 2px solid transparent; }
        .tab-btn.active { color var(--text); border-bottom 2px solid var(--text); font-weight 500; }
        .tab-content { display none; }
        .tab-content.active { display block; animation fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity 0; } to { opacity 1; } }
        .card { background var(--card); border 1px solid var(--border); border-radius 4px; padding 30px; margin-bottom 20px; box-shadow 0 2px 8px rgba(0,0,0,0.02);}
        .card h2 { margin-top 0; font-size 1.2rem; border-bottom 1px solid var(--border); padding-bottom 10px; margin-bottom 20px;}
        .grid { display grid; grid-template-columns 1fr 1fr; gap 15px; }
        .form-group { margin-bottom 15px; }
        label { display block; font-size 0.9rem; color var(--muted); margin-bottom 5px; }
        input, select, textarea { width 100%; padding 10px; border 1px solid var(--border); border-radius 3px; box-sizing border-box; font-size 1rem; color var(--text);}
        inputfocus, selectfocus, textareafocus { border-color var(--btn); outline none; }
        .btn { background var(--btn); color #fff; border none; padding 10px 20px; font-size 1rem; border-radius 3px; cursor pointer; letter-spacing 1px;}
        .btnhover { opacity 0.9; }
        .btn-small { padding 5px 10px; font-size 0.85rem; }
        .btn-danger { background white; color var(--danger); border 1px solid var(--danger); }
        .alert { padding 15px; margin-bottom 20px; background #f0f7e6; color var(--success); border 1px solid #d4e5c2; border-radius 3px;}
        table { width 100%; border-collapse collapse; font-size 0.95rem;}
        th, td { text-align left; padding 12px; border-bottom 1px solid var(--border); vertical-align top; }
        .lang-selector { position absolute; top 0; right 0; }
        .code-wrapper { position relative; margin-top 10px; }
        pre { background #272822; color #f8f8f2; padding 20px 15px 15px 15px; border-radius 4px; overflow auto; font-family monospace; font-size 0.9rem; margin0;}
        .copy-btn { position absolute; top 8px; right 8px; background rgba(255,255,255,0.2); color #fff; border 1px solid rgba(255,255,255,0.4); padding 4px 10px; font-size 0.8rem; border-radius 3px; cursor pointer;}
        .copy-btnhover { background rgba(255,255,255,0.3); border-color #fff; }
        .top-settings-bar { background #f3f3f3; padding 15px 20px; border-radius 4px; margin-bottom 20px; border 1px solid var(--border); }
        .inline-form { display flex; align-items center; gap 15px; }
    style
head
body
    div class=container
        div class=lang-selector
            form action=change_lang method=POST id=langForm style=margin0;
                select name=lang onchange=document.cookie='lang='+this.value+'; path=; max-age=31536000'; this.form.submit();
                    option value=zh {% if lang=='zh' %}selected{% endif %}🇹🇼 繁體中文option
                    option value=en {% if lang=='en' %}selected{% endif %}🇺🇸 Englishoption
                    option value=vi {% if lang=='vi' %}selected{% endif %}🇻🇳 Tiếng Việtoption
                select
            form
        div
        h1 style=margin-bottom 30px;{{ t.title }}h1
        
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              div class=alert{{ message }}div
            {% endfor %}
          {% endif %}
        {% endwith %}
        
        div class=tabs
            button class=tab-btn active onclick=openTab('ConfigTab', this){{ t.tab_nodes }}button
            button class=tab-btn onclick=openTab('DocsTab', this){{ t.tab_scripts }}button
            button class=tab-btn onclick=openTab('RestoreTab', this){{ t.tab_restore }}button
        div

        div id=ConfigTab class=tab-content active
            div class=top-settings-bar
                h2 style=bordernone; margin0 0 10px 0; font-size1.1rem;{{ t.global_settings }}h2
                form action=update_globals method=POST class=inline-form
                    label{{ t.ext_port }} input type=number name=ext_port value={{ ext_port }} style=width80px; padding6px; margin-left5px; requiredlabel
                    label{{ t.global_mount }} input type=text name=global_host_mount value={{ global_host_mount }} style=width200px; padding6px; margin-left5px; requiredlabel
                    button type=submit class=btn btn-small{{ t.apply_global }}button
                form
                div style=font-size 0.85rem; color var(--muted); margin-top 10px;{{ t.hint_global }}div
            div

            div class=card id=formCard
                div class=form-header
                    h2 id=formTitle{{ t.add_node }}h2
                    button type=button class=btn btn-small style=displaynone; id=btnCancelEdit onclick=resetForm(){{ t.cancel_edit }}button
                div
                form action=save method=POST id=configForm
                    input type=hidden name=id id=f_id
                    
                    div class=grid
                        div class=form-group
                            label{{ t.protocol }}label
                            select name=proto id=f_proto onchange=toggleUI() required
                                option value=smbSMB  CIFSoption
                                option value=nfsNFSoption
                                option value=rcloneRclone (CloudSFTP)option
                            select
                        div
                        div class=form-group
                            label{{ t.node_name }}label
                            input type=text name=name id=f_name required
                        div
                    div
                    
                    div class=form-group
                        label{{ t.desc }}label
                        input type=text name=description id=f_desc placeholder={{ t.desc_ph }} required
                    div

                    div class=grid
                        div class=form-group id=wrap_ip
                            label{{ t.ip }}label
                            input type=text name=server_ip id=f_ip
                        div
                        div class=form-group
                            label{{ t.port }}label
                            input type=number name=port id=f_port placeholder=22, 445, etc.
                        div
                    div
                    div class=form-group
                        label{{ t.remote_path }}label
                        input type=text name=remote_path id=f_path placeholder={{ t.remote_path_ph }}
                    div

                    div class=grid id=wrap_auth
                        div class=form-group
                            label{{ t.username }}label
                            input type=text name=username id=f_user
                        div
                        div class=form-group
                            label{{ t.password }}label
                            input type=password name=password id=f_pass
                            small style=colorvar(--muted); displaynone; margin-top5px; id=rclone_pass_hint{{ t.rclone_pass_hint }}small
                        div
                    div

                    div id=wrap_rclone style=displaynone;
                        div class=form-group
                            label{{ t.rclone_type }}label
                            input type=text name=rclone_type id=f_rtype placeholder={{ t.rclone_type_ph }}
                        div
                        div class=form-group
                            label{{ t.rclone_args }}label
                            textarea name=rclone_args id=f_rargs rows=2 placeholder={{ t.rclone_args_ph }}textarea
                        div
                    div

                    div style=margin-top 10px;
                        button type=submit class=btn id=btnSubmit{{ t.btn_save }}button
                        button type=button class=btn style=background#eee; color#333; displaynone; margin-left10px; id=btnCancel onclick=resetForm(){{ t.cancel_edit }}button
                    div
                form
            div

            div class=card
                h2{{ t.list_title }}h2
                table
                    theadtrth{{ t.col_proto }}thth{{ t.col_name }}thth{{ t.col_ip }}thth style=width 120px;{{ t.col_action }}thtrthead
                    tbody
                        {% for item in servers %}
                        tr
                            tdspan style=background#eee; padding3px 8px; border-radius12px; font-size0.8rem; text-transformuppercase;{{ item.proto }}spantd
                            tdstrong{{ item.name }}strongbrsmall style=colorvar(--muted);{{ item.description }}smalltd
                            td
                                div style=margin-bottom 4px;span style=colorvar(--muted); font-size0.8rem;{{ t.remote_target }}span {{ item.server_ip or '-' }}{% if item.port %}{{ item.port }}{% endif %}{{ item.remote_path }}div
                                divspan style=colorvar(--muted); font-size0.8rem;{{ t.local_path }}span {{ global_host_mount }}{{ item.name }}div
                            td
                            td
                                button class=btn style=padding4px 8px; font-size0.8rem; onclick='edit({{ item  tojson  safe }})'{{ t.btn_edit }}button
                                form action=delete{{ item.id }} method=POST onsubmit=return confirm('{{ t.confirm_del }}'); style=displayinline;
                                    button type=submit class=btn btn-danger style=padding4px 8px; font-size0.8rem;{{ t.btn_delete }}button
                                form
                            td
                        tr
                        {% else %}
                        trtd colspan=4 style=text-aligncenter; colorvar(--muted);{{ t.no_nodes }}tdtr
                        {% endfor %}
                    tbody
                table
            div
        div

        div id=DocsTab class=tab-content
            div class=card
                h2{{ t.script_1_title }}h2
                p{{ t.script_1_desc }}p
                p style=color var(--muted); font-size 0.9rem;{{ t.fuse_hint  safe }}p
                div class=code-wrapperbutton class=copy-btn onclick=copyCode(this, 'code-startup'){{ t.btn_copy_script }}buttonpre id=code-startup{{ startup_content }}prediv
            div
            div class=card
                h2{{ t.script_2_title }}h2
                p{{ t.script_2_desc }}p
                div class=code-wrapperbutton class=copy-btn onclick=copyCode(this, 'code-shutdown'){{ t.btn_copy_script }}buttonpre id=code-shutdown{{ shutdown_content }}prediv
            div
            div class=card
                h2{{ t.script_3_title }}h2
                div class=code-wrapperbutton class=copy-btn onclick=copyCode(this, 'code-yaml'){{ t.btn_copy_yaml }}buttonpre id=code-yaml{{ compose_content }}prediv
            div
        div

        div id=RestoreTab class=tab-content
            div class=card style=line-height 1.6;
                h2{{ t.restore_card_title }}h2
                p{{ t.restore_p1 }}p
                div class=code-wrapperpre style=color #a6e22e; font-weight bold; font-size 1.05rem;{{ t.restore_path }}prediv
                p style=margin-top 15px;{{ t.restore_p2  safe }}p
                p{{ t.restore_p3  safe }}p
            div
            
            div class=card style=line-height 1.6;
                h2{{ t.obscure_title }}h2
                p{{ t.obscure_p1 }}p
                div class=code-wrapper
                    button class=copy-btn onclick=copyCode(this, 'code-obscure'){{ t.btn_copy_script }}button
                    pre id=code-obscure{{ t.obscure_cmd }}pre
                div
                p style=margin-top 15px;{{ t.obscure_p2  safe }}p
            div
        div
    div

    script
        function openTab(name, btn) {
            document.querySelectorAll('.tab-content').forEach(d = d.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b = b.classList.remove('active'));
            document.getElementById(name).classList.add('active');
            btn.classList.add('active');
        }

        function toggleUI() {
            const p = document.getElementById('f_proto').value;
            const wAuth = document.getElementById('wrap_auth');
            const wRclone = document.getElementById('wrap_rclone');
            const hintPass = document.getElementById('rclone_pass_hint');
            
            ['f_ip', 'f_path', 'f_user', 'f_pass', 'f_rtype'].forEach(id = document.getElementById(id).required = false);

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
            document.getElementById('f_ip').value = d.server_ip  '';
            document.getElementById('f_port').value = d.port  '';
            document.getElementById('f_path').value = d.remote_path  '';
            document.getElementById('f_user').value = d.username  '';
            document.getElementById('f_pass').value = d.password  '';
            document.getElementById('f_rtype').value = d.rclone_type  '';
            document.getElementById('f_rargs').value = d.rclone_args  '';
            
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
                navigator.clipboard.writeText(text).then(()=success(btn)).catch(()=fallback(text, btn));
            } else { fallback(text, btn); }
        }
        function success(btn) {
            const org = btn.innerText; btn.innerText = '{{ t.copied }}';
            btn.style.background = 'var(--success)'; btn.style.borderColor = 'var(--success)';
            setTimeout(() = { btn.innerText = org; btn.style.background = ''; btn.style.borderColor = ''; }, 2000);
        }
        function fallback(text, btn) {
            const ta = document.createElement(textarea); ta.value = text;
            ta.style.position=fixed; ta.style.opacity=0; document.body.appendChild(ta);
            ta.select(); document.execCommand('copy'); ta.remove(); success(btn);
        }

        toggleUI();
    script
body
html


@app.route('')
def index()
    lang = get_locale()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['zh'])
    with sqlite3.connect(DB_PATH) as conn
        conn.row_factory = sqlite3.Row
        servers = [dict(r) for r in conn.execute(SELECT  FROM servers ORDER BY id DESC)]
        ext_port = conn.execute(SELECT value FROM settings WHERE key='ext_port').fetchone()['value']
        global_mount = conn.execute(SELECT value FROM settings WHERE key='global_host_mount').fetchone()['value']
    
    def read_f(p) return open(p).read() if os.path.exists(p) else 
    return render_template_string(HTML_TEMPLATE, servers=servers, lang=lang, t=t, 
                                  ext_port=ext_port, global_host_mount=global_mount,
                                  startup_content=read_f(STARTUP_FILE), 
                                  shutdown_content=read_f(SHUTDOWN_FILE),
                                  compose_content=read_f(COMPOSE_FILE))

@app.route('change_lang', methods=['POST'])
def change_lang()
    lang = request.form.get('lang', 'zh')
    sync_db_to_files(lang)
    return redirect('')

@app.route('update_globals', methods=['POST'])
def update_globals()
    t = TRANSLATIONS.get(get_locale(), TRANSLATIONS['zh'])
    with sqlite3.connect(DB_PATH) as conn
        conn.execute(UPDATE settings SET value= WHERE key='ext_port', (request.form.get('ext_port'),))
        conn.execute(UPDATE settings SET value= WHERE key='global_host_mount', (request.form.get('global_host_mount').rstrip(''),))
    sync_db_to_files()
    flash(t['flash_global_ok'])
    return redirect('')

@app.route('save', methods=['POST'])
def save()
    t = TRANSLATIONS.get(get_locale(), TRANSLATIONS['zh'])
    port_val = request.form.get('port')
    
    data = {
        'id' request.form.get('id'), 'proto' request.form.get('proto'),
        'name' request.form.get('name').strip(), 'description' request.form.get('description'),
        'server_ip' request.form.get('server_ip', ''), 'remote_path' request.form.get('remote_path', ''),
        'username' request.form.get('username', ''), 'password' request.form.get('password', ''),
        'rclone_type' request.form.get('rclone_type', ''), 'rclone_args' request.form.get('rclone_args', ''),
        'port' int(port_val) if port_val and port_val.isdigit() else 0
    }
    
    with sqlite3.connect(DB_PATH) as conn
        try
            if data['id']
                conn.execute(UPDATE servers SET proto=proto, name=name, description=description, server_ip=server_ip, remote_path=remote_path, username=username, password=password, rclone_type=rclone_type, rclone_args=rclone_args, port=port WHERE id=id, data)
                flash(t['flash_update_ok'].format(name=data['name']))
            else
                conn.execute(INSERT INTO servers (proto, name, description, server_ip, remote_path, username, password, rclone_type, rclone_args, port) VALUES (proto, name, description, server_ip, remote_path, username, password, rclone_type, rclone_args, port), data)
                flash(t['flash_add_ok'].format(name=data['name']))
        except sqlite3.IntegrityError
            flash(t['flash_name_err'].format(name=data['name']), 'error')
            
    sync_db_to_files()
    return redirect('')

@app.route('deleteintrecord_id', methods=['POST'])
def delete(record_id)
    t = TRANSLATIONS.get(get_locale(), TRANSLATIONS['zh'])
    with sqlite3.connect(DB_PATH) as conn
        conn.execute(DELETE FROM servers WHERE id=, (record_id,))
    sync_db_to_files()
    flash(t['flash_del_ok'])
    return redirect('')

if __name__ == '__main__'
    app.run(host='0.0.0.0', port=5000, debug=True)