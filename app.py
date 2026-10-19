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
        'title': 'backrest docker 產生器',
        'tab_nodes': '遠端節點管理',
        'tab_scripts': '維運腳本 (啟動/停用)',
        'tab_restore': '還原說明 (Restore)',
        'global_settings': '系統全域設定 (Global Settings)',
        'ext_port': '外部 Port:',
        'global_mount': '宿主機來源目錄 (/data/source):',
        'global_dest': '宿主機目標目錄 (/data/dest):',
        'tz_label': '時區 (TZ):',
        'apply_global': '套用全域設定',
        'hint_global': '💡 提示：新增、修改、刪除節點或套用設定時皆會自動更新 Docker Compose 與腳本檔案；亦可點擊上方按鈕手動重新產生。',
        'add_node': '新增遠端連線節點',
        'cancel_edit': '取消編輯',
        'btn_examples': '📖 填寫範例說明',
        'modal_examples_title': '遠端連線節點 (SMB / NFS / Rclone) 填寫範例說明',
        'modal_close': '關閉視窗',
        'ex_field': '欄位名稱',
        'ex_val': '填寫範例',
        'ex_note': '說明',
        'ex_smb_title': '1. SMB / CIFS 填寫範例 (Windows 共用資料夾 / NAS)',
        'ex_smb_desc': '適用於 Windows 芳鄰或 NAS 的 SMB/CIFS 共用目錄（唯讀掛載）。',
        'ex_nfs_title': '2. NFS 填寫範例 (Linux / NAS NFS Export)',
        'ex_nfs_desc': '適用於 Linux 或 NAS 匯出的 NFS 目錄（免填帳號密碼，由 NFS 伺服器端 IP 權限控管）。',
        'ex_rclone_title': '3. Rclone 填寫範例 (SFTP / 雲端儲存)',
        'ex_rclone_desc': '適用於 SFTP 或各類雲端硬碟（透過 Rclone FUSE 唯讀掛載）。注意：密碼必須填入 rclone obscure 加密後的字串！',
        'ex_none_needed': '(免填)',
        'ex_optional_port': '(選填，可留空使用預設值)',
        'protocol': '通訊協定 (Protocol)',
        'node_name': '宿主機掛載子目錄名稱 (對應容器 /data/source/<此名稱>)',
        'node_name_hint': '宿主機掛載路徑：<code><span class="dyn-host-mount">{mount}</span>/<span class="dyn-node-name">&lt;名稱&gt;</span></code><br>容器內路徑：<code>/data/source/<span class="dyn-node-name">&lt;名稱&gt;</span></code>',
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
        'btn_sync_files': '🔄 產生 Docker Compose 與腳本檔案',
        'list_title': '現有連線節點清單',
        'col_proto': '協定',
        'col_name': '識別名稱',
        'col_ip': '遠端與本地掛載對應',
        'remote_target': '遠端來源',
        'local_path': '本地',
        'container_path': '容器',
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
        'flash_sync_ok': '✅ Docker Compose 與腳本檔案已成功產生！',
        'flash_global_db_only': '✅ 全域設定已更新，並已自動重新產生 Docker Compose 與腳本檔案！',
        'flash_update_db_only': '✅ 節點「{name}」已更新，並已自動重新產生 Docker Compose 與腳本檔案！',
        'flash_add_ok': '✅ 成功新增節點「{name}」！(Docker Compose 與腳本檔案已自動更新)',
        'flash_name_err': '❌ 名稱「{name}」重複。',
        'flash_del_db_only': '🗑️ 節點已移除，並已自動重新產生 Docker Compose 與腳本檔案！',
        'restore_card_title': 'Backrest 快照還原注意事項',
        'restore_path': '/data/dest/自訂目錄名稱',
        'restore_p1': '還原時請務必指定目標目錄：',
        'restore_p2': '⚠️ 目錄必須為空，否則還原會失敗。',
        'restore_p3': '還原後檔案位於宿主機目標目錄: <code class="dyn-host-dest">{dest}</code>（對應容器內 <code>/data/dest</code>；備份來源則位於宿主機 <code class="dyn-host-mount">{mount}</code>，對應容器內 <code>/data/source</code>）。',
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
        'title': 'Backrest Docker Generator',
        'tab_nodes': 'Remote Nodes',
        'tab_scripts': 'Ops Scripts',
        'tab_restore': 'Restore Guide',
        'global_settings': 'Global Settings',
        'ext_port': 'Ext Port:',
        'global_mount': 'Host Source Dir (/data/source):',
        'global_dest': 'Host Target Dir (/data/dest):',
        'tz_label': 'Timezone (TZ):',
        'apply_global': 'Apply',
        'hint_global': '💡 Hint: Docker Compose and script files are auto-generated whenever settings or nodes change. You can also click the button above to regenerate manually.',
        'add_node': 'Add Node',
        'cancel_edit': 'Cancel',
        'btn_examples': '📖 Input Examples',
        'modal_examples_title': 'Remote Node (SMB / NFS / Rclone) Input Examples',
        'modal_close': 'Close',
        'ex_field': 'Field',
        'ex_val': 'Example Value',
        'ex_note': 'Note',
        'ex_smb_title': '1. SMB / CIFS Example (Windows Share / NAS)',
        'ex_smb_desc': 'Mounts a remote SMB/CIFS shared folder read-only.',
        'ex_nfs_title': '2. NFS Example (Linux / NAS NFS Export)',
        'ex_nfs_desc': 'Mounts an NFS export read-only (no username/password needed; controlled by server export IP rules).',
        'ex_rclone_title': '3. Rclone Example (SFTP / Cloud Storage)',
        'ex_rclone_desc': 'Mounts via Rclone FUSE read-only. Note: Password must be obscured using rclone obscure!',
        'ex_none_needed': '(Not required)',
        'ex_optional_port': '(Optional, leave blank for default)',
        'protocol': 'Protocol',
        'node_name': 'Host Mount Subfolder Name (Maps to /data/source/<name>)',
        'node_name_hint': 'Host Mount: <code><span class="dyn-host-mount">{mount}</span>/<span class="dyn-node-name">&lt;name&gt;</span></code><br>Container Path: <code>/data/source/<span class="dyn-node-name">&lt;name&gt;</span></code>',
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
        'btn_sync_files': '🔄 Generate Docker Compose & Scripts',
        'list_title': 'Existing Nodes',
        'col_proto': 'Proto',
        'col_name': 'Name',
        'col_ip': 'Remote & Local Mappings',
        'remote_target': 'Remote',
        'local_path': 'Local',
        'container_path': 'Container',
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
        'flash_sync_ok': '✅ Docker Compose and script files generated successfully!',
        'flash_global_db_only': '✅ Global settings updated and Docker Compose & scripts regenerated!',
        'flash_update_db_only': '✅ Node "{name}" updated and Docker Compose & scripts regenerated!',
        'flash_add_ok': '✅ Node "{name}" added! (Docker Compose & scripts auto-generated)',
        'flash_name_err': '❌ Duplicate name "{name}".',
        'flash_del_db_only': '🗑️ Node removed and Docker Compose & scripts regenerated!',
        'restore_card_title': 'Backrest Restore Guide',
        'restore_path': '/data/dest/custom_folder',
        'restore_p1': 'Specify target path when restoring:',
        'restore_p2': '⚠️ Folder must be empty or new.',
        'restore_p3': 'Restored files are stored in host target directory: <code class="dyn-host-dest">{dest}</code> (maps to container <code>/data/dest</code>; host source <code class="dyn-host-mount">{mount}</code> maps to container <code>/data/source</code>).',
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
        'title': 'Trình tạo Docker Backrest',
        'tab_nodes': 'Quản lý Node Từ xa',
        'tab_scripts': 'Kịch bản Vận hành',
        'tab_restore': 'Hướng dẫn Khôi phục',
        'global_settings': 'Cài đặt Toàn cục (Global)',
        'ext_port': 'Port Ngoài:',
        'global_mount': 'Thư mục Nguồn Host (/data/source):',
        'global_dest': 'Thư mục Đích Host (/data/dest):',
        'tz_label': 'Múi giờ (TZ):',
        'apply_global': 'Áp dụng',
        'hint_global': '💡 Lưu ý: Tệp Docker Compose và kịch bản sẽ tự động cập nhật khi thêm/sửa/xóa. Bạn cũng có thể nhấp nút phía trên để tạo lại thủ công.',
        'add_node': 'Thêm Node',
        'cancel_edit': 'Hủy',
        'btn_examples': '📖 Ví dụ nhập liệu',
        'modal_examples_title': 'Hướng dẫn & Ví dụ nhập Node (SMB / NFS / Rclone)',
        'modal_close': 'Đóng',
        'ex_field': 'Trường thông tin',
        'ex_val': 'Ví dụ điền',
        'ex_note': 'Ghi chú',
        'ex_smb_title': '1. Ví dụ SMB / CIFS (Thư mục chia sẻ Windows / NAS)',
        'ex_smb_desc': 'Dùng cho thư mục chia sẻ SMB/CIFS từ Windows hoặc NAS (mount chỉ đọc).',
        'ex_nfs_title': '2. Ví dụ NFS (Linux / NAS NFS Export)',
        'ex_nfs_desc': 'Dùng cho thư mục xuất NFS từ Linux hoặc NAS (không cần tài khoản/mật khẩu).',
        'ex_rclone_title': '3. Ví dụ Rclone (SFTP / Đám mây)',
        'ex_rclone_desc': 'Dùng cho SFTP hoặc lưu trữ đám mây qua Rclone FUSE. Lưu ý: Mật khẩu phải mã hóa bằng rclone obscure!',
        'ex_none_needed': '(Không cần nhập)',
        'ex_optional_port': '(Tùy chọn, để trống dùng mặc định)',
        'protocol': 'Giao thức',
        'node_name': 'Tên thư mục con Mount trên Host (Ánh xạ tới /data/source/<tên>)',
        'node_name_hint': 'Đường dẫn Host: <code><span class="dyn-host-mount">{mount}</span>/<span class="dyn-node-name">&lt;tên&gt;</span></code><br>Đường dẫn Container: <code>/data/source/<span class="dyn-node-name">&lt;tên&gt;</span></code>',
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
        'btn_sync_files': '🔄 Tạo tệp Docker Compose & Kịch bản',
        'list_title': 'Danh sách Node',
        'col_proto': 'Giao thức',
        'col_name': 'Định danh',
        'col_ip': 'Ánh xạ Từ xa & Cục bộ',
        'remote_target': 'Từ xa',
        'local_path': 'Cục bộ',
        'container_path': 'Container',
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
        'flash_sync_ok': '✅ Đã tạo tệp Docker Compose và kịch bản thành công!',
        'flash_global_db_only': '✅ Đã cập nhật cài đặt và tự động tạo lại tệp Docker Compose & kịch bản!',
        'flash_update_db_only': '✅ Đã cập nhật node "{name}" và tự động tạo lại tệp Docker Compose & kịch bản!',
        'flash_add_ok': '✅ Đã thêm node "{name}"! (Tự động tạo tệp Docker Compose & kịch bản)',
        'flash_name_err': '❌ Lỗi: Tên "{name}" đã tồn tại.',
        'flash_del_db_only': '🗑️ Đã xóa node và tự động tạo lại tệp Docker Compose & kịch bản!',
        'restore_card_title': 'Lưu ý khi Khôi phục',
        'restore_path': '/data/dest/ten_thu_muc',
        'restore_p1': 'Phải đặt đường dẫn đích thành:',
        'restore_p2': '⚠️ Thư mục này phải trống.',
        'restore_p3': 'Tệp sau khi khôi phục nằm tại thư mục đích trên host: <code class="dyn-host-dest">{dest}</code> (ánh xạ tới <code>/data/dest</code>; thư mục nguồn host <code class="dyn-host-mount">{mount}</code> ánh xạ tới <code>/data/source</code>).',
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
        conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('global_host_dest', '/mnt/dest')")
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
        dest_row = conn.execute("SELECT value FROM settings WHERE key='global_host_dest'").fetchone()
        global_host_dest = dest_row['value'] if dest_row else '/mnt/dest'
        tz = conn.execute("SELECT value FROM settings WHERE key='tz'").fetchone()
        tz_val = tz['value'] if tz else ""

    # 1. YAML (加入 profiles: ["manual"], restart: "no", 及 TZ 環境變數)
    if os.path.exists(COMPOSE_FILE):
        with open(COMPOSE_FILE, 'r', encoding='utf-8') as f: compose_data = yaml.load(f) or {}
    else: compose_data = {'version': '3.8', 'services': {}}
    
    compose_data.setdefault('services', {})
    
    backrest_config = {
        'image': 'garethgeorge/backrest:latest',
        'container_name': 'backrest',
        'restart': 'no',  
        'profiles': ['manual'],
        'ports': [f"{ext_port}:9898"],
        'volumes': ['./backrest_config:/config', f"{global_host_dest}:/data/dest", f"{global_host_mount}:/data/source:ro"]
    }
    
    if tz_val.strip():
        backrest_config['environment'] = [f"TZ={tz_val.strip()}"]

    compose_data['services']['backrest'] = backrest_config
    
    if 'volumes' in compose_data:
        if isinstance(compose_data['volumes'], dict):
            compose_data['volumes'].pop('backrest_data', None)
        if not compose_data['volumes']:
            del compose_data['volumes']
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
        f'sudo mkdir -p {global_host_dest}',
        'docker compose --profile manual up -d',
        f'echo "{t["sh_svc_done"]}"'
    ])
    shutdown.append(f'echo "{t["sh_umount_done"]}"')

    with open(STARTUP_FILE, 'w', encoding='utf-8') as f: f.write("\n".join(startup))
    with open(SHUTDOWN_FILE, 'w', encoding='utf-8') as f: f.write("\n".join(shutdown))
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
        .container { width: 100%; max-width: 1160px; position: relative; }
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
        .inline-form { display: flex; flex-direction: column; gap: 12px; }
        .inline-row { display: flex; flex-wrap: nowrap; align-items: center; gap: 15px; }
        .inline-row label { display: inline-flex; align-items: center; white-space: nowrap; margin-bottom: 0; }
        .form-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 20px; }
        .form-header h2 { border-bottom: none; padding-bottom: 0; margin-bottom: 0; }
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; justify-content: center; align-items: center; padding: 20px; box-sizing: border-box; }
        .modal-overlay.active { display: flex; animation: fadeIn 0.2s; }
        .modal-box { background: var(--card); width: 100%; max-width: 820px; max-height: 85vh; border-radius: 6px; box-shadow: 0 8px 30px rgba(0,0,0,0.2); display: flex; flex-direction: column; overflow: hidden; }
        .modal-header { display: flex; justify-content: space-between; align-items: center; padding: 18px 25px; border-bottom: 1px solid var(--border); background: #f5f6f8; }
        .modal-header h2 { margin: 0; font-size: 1.15rem; border: none; padding: 0; }
        .modal-body { padding: 20px 25px; overflow-y: auto; line-height: 1.5; }
        .ex-section { margin-bottom: 24px; border: 1px solid var(--border); border-radius: 4px; padding: 15px 18px; background: #fafafa; }
        .ex-section:last-child { margin-bottom: 0; }
        .ex-section h3 { margin: 0 0 6px 0; font-size: 1.05rem; color: #2c4a7c; }
        .ex-table { width: 100%; border-collapse: collapse; margin-top: 10px; background: #fff; font-size: 0.9rem; }
        .ex-table th, .ex-table td { border: 1px solid var(--border); padding: 8px 10px; }
        .ex-table th { background: #f0f2f5; width: 32%; }
        .ex-code { font-family: monospace; background: #eef2f7; padding: 2px 6px; border-radius: 3px; color: #b52b27; }
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
                    <form action="/sync_files" method="POST" style="margin:0;" onsubmit="attachGlobals(this)">
                        <button type="submit" class="btn" style="background: #4a6fa5;">{{ t.btn_sync_files }}</button>
                    </form>
                </div>
                <form action="/update_globals" method="POST" class="inline-form" id="globalForm">
                    <div class="inline-row">
                        <label>{{ t.ext_port }} <input type="number" name="ext_port" id="g_ext_port" value="{{ ext_port }}" oninput="syncDynamicPaths()" onchange="autoSaveGlobals()" style="width:75px; padding:6px; margin-left:5px;" required></label>
                        <label>{{ t.global_mount }} <input type="text" name="global_host_mount" id="g_host_mount" value="{{ global_host_mount }}" oninput="syncDynamicPaths()" onchange="autoSaveGlobals()" style="width:140px; padding:6px; margin-left:5px;" required></label>
                        <label>{{ t.global_dest }} <input type="text" name="global_host_dest" id="g_host_dest" value="{{ global_host_dest }}" oninput="syncDynamicPaths()" onchange="autoSaveGlobals()" style="width:140px; padding:6px; margin-left:5px;" required></label>
                    </div>
                    <div class="inline-row">
                        <label>{{ t.tz_label }} <input type="text" name="tz" id="g_tz" value="{{ tz }}" onchange="autoSaveGlobals()" style="width:140px; padding:6px; margin-left:5px;" placeholder="Asia/Taipei"></label>
                        <button type="submit" class="btn btn-small">{{ t.apply_global }}</button>
                    </div>
                </form>
                <div style="font-size: 0.85rem; color: var(--muted); margin-top: 10px;">{{ t.hint_global }}</div>
            </div>

            <div class="card" id="formCard">
                <div class="form-header">
                    <h2 id="formTitle">{{ t.add_node }}</h2>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <button type="button" class="btn btn-small" style="background: #4a6fa5;" onclick="openExampleModal()">{{ t.btn_examples }}</button>
                        <button type="button" class="btn btn-small" style="display:none;" id="btnCancelEdit" onclick="resetForm()">{{ t.cancel_edit }}</button>
                    </div>
                </div>
                <form action="/save" method="POST" id="configForm" onsubmit="attachGlobals(this)">
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
                            <input type="text" name="name" id="f_name" oninput="syncDynamicPaths()" required>
                            <small style="color:var(--muted); display:block; margin-top:5px; line-height:1.6;">{{ t.node_name_hint.format(mount=global_host_mount) | safe }}</small>
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
                                <div style="white-space: nowrap;"><span style="color:var(--muted); font-size:0.8rem;">{{ t.local_path }}:</span> <span class="dyn-host-mount">{{ global_host_mount }}</span>/{{ item.name }} -&gt; <span style="color:var(--muted); font-size:0.8rem;">{{ t.container_path }}：</span>/data/source/{{ item.name }}</div>
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
                <p>{{ t.restore_p3.format(dest=global_host_dest, mount=global_host_mount) | safe }}</p>
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

    <div id="exampleModal" class="modal-overlay" onclick="if(event.target===this) closeExampleModal()">
        <div class="modal-box">
            <div class="modal-header">
                <h2>{{ t.modal_examples_title }}</h2>
                <button type="button" class="btn btn-small" onclick="closeExampleModal()">{{ t.modal_close }} ✕</button>
            </div>
            <div class="modal-body">
                <div class="ex-section">
                    <h3>{{ t.ex_smb_title }}</h3>
                    <div style="color: var(--muted); font-size: 0.9rem;">{{ t.ex_smb_desc }}</div>
                    <table class="ex-table">
                        <thead><tr><th>{{ t.ex_field }}</th><th>{{ t.ex_val }}</th></tr></thead>
                        <tbody>
                            <tr><td>{{ t.protocol }}</td><td><span class="ex-code">SMB / CIFS</span></td></tr>
                            <tr><td>{{ t.node_name }}</td><td><span class="ex-code">nas_smb</span> (<code><span class="dyn-host-mount">{{ global_host_mount }}</span>/nas_smb</code> &rarr; <code>/data/source/nas_smb</code>)</td></tr>
                            <tr><td>{{ t.desc }}</td><td>{{ t.desc_ph }}</td></tr>
                            <tr><td>{{ t.ip }}</td><td><span class="ex-code">192.168.1.100</span></td></tr>
                            <tr><td>{{ t.port }}</td><td><span class="ex-code">445</span> {{ t.ex_optional_port }}</td></tr>
                            <tr><td>{{ t.remote_path }}</td><td><span class="ex-code">SharedFolder/SOP</span></td></tr>
                            <tr><td>{{ t.username }} / {{ t.password }}</td><td><span class="ex-code">backup_user</span> / <span class="ex-code">PlainTextPassword</span></td></tr>
                        </tbody>
                    </table>
                </div>

                <div class="ex-section">
                    <h3>{{ t.ex_nfs_title }}</h3>
                    <div style="color: var(--muted); font-size: 0.9rem;">{{ t.ex_nfs_desc }}</div>
                    <table class="ex-table">
                        <thead><tr><th>{{ t.ex_field }}</th><th>{{ t.ex_val }}</th></tr></thead>
                        <tbody>
                            <tr><td>{{ t.protocol }}</td><td><span class="ex-code">NFS</span></td></tr>
                            <tr><td>{{ t.node_name }}</td><td><span class="ex-code">linux_nfs</span> (<code><span class="dyn-host-mount">{{ global_host_mount }}</span>/linux_nfs</code> &rarr; <code>/data/source/linux_nfs</code>)</td></tr>
                            <tr><td>{{ t.desc }}</td><td>Linux Server NFS Backup</td></tr>
                            <tr><td>{{ t.ip }}</td><td><span class="ex-code">192.168.1.200</span></td></tr>
                            <tr><td>{{ t.port }}</td><td><span class="ex-code">2049</span> {{ t.ex_optional_port }}</td></tr>
                            <tr><td>{{ t.remote_path }}</td><td><span class="ex-code">/volume1/data</span></td></tr>
                            <tr><td>{{ t.username }} / {{ t.password }}</td><td>{{ t.ex_none_needed }}</td></tr>
                        </tbody>
                    </table>
                </div>

                <div class="ex-section">
                    <h3>{{ t.ex_rclone_title }}</h3>
                    <div style="color: var(--muted); font-size: 0.9rem;">{{ t.ex_rclone_desc }}</div>
                    <table class="ex-table">
                        <thead><tr><th>{{ t.ex_field }}</th><th>{{ t.ex_val }}</th></tr></thead>
                        <tbody>
                            <tr><td>{{ t.protocol }}</td><td><span class="ex-code">Rclone (Cloud/SFTP)</span></td></tr>
                            <tr><td>{{ t.node_name }}</td><td><span class="ex-code">remote_sftp</span> (<code><span class="dyn-host-mount">{{ global_host_mount }}</span>/remote_sftp</code> &rarr; <code>/data/source/remote_sftp</code>)</td></tr>
                            <tr><td>{{ t.desc }}</td><td>Ubuntu SFTP Server Backup</td></tr>
                            <tr><td>{{ t.ip }} / {{ t.port }}</td><td><span class="ex-code">192.168.1.50</span> / <span class="ex-code">22</span></td></tr>
                            <tr><td>{{ t.remote_path }}</td><td><span class="ex-code">/home/ubuntu/backup_data</span></td></tr>
                            <tr><td>{{ t.username }}</td><td><span class="ex-code">ubuntu</span></td></tr>
                            <tr><td>{{ t.password }}</td><td><span class="ex-code">v1M_xxxxxx...</span> (<code>{{ t.obscure_cmd }}</code>)</td></tr>
                            <tr><td>{{ t.rclone_type }}</td><td><span class="ex-code">sftp</span></td></tr>
                            <tr><td>{{ t.rclone_args }}</td><td><span class="ex-code">use_temp_mutime = false</span></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentScriptMount = {{ global_host_mount | tojson }};
        let currentScriptDest = {{ global_host_dest | tojson }};
        let currentScriptPort = {{ ext_port | tojson }};

        function syncDynamicPaths() {
            const mountInput = document.getElementById('g_host_mount');
            const destInput = document.getElementById('g_host_dest');
            const portInput = document.getElementById('g_ext_port');
            const nameInput = document.getElementById('f_name');
            const mountVal = ((mountInput && mountInput.value.trim()) ? mountInput.value.trim().replace(/[/]+$/, '') : '/mnt/source') || '/';
            const destVal = ((destInput && destInput.value.trim()) ? destInput.value.trim().replace(/[/]+$/, '') : '/mnt/dest') || '/';
            const portVal = (portInput && portInput.value.trim()) ? portInput.value.trim() : currentScriptPort;
            const nameVal = (nameInput && nameInput.value.trim()) ? nameInput.value.trim() : '<name>';

            document.querySelectorAll('.dyn-host-mount').forEach(el => { el.textContent = mountVal; });
            document.querySelectorAll('.dyn-host-dest').forEach(el => { el.textContent = destVal; });
            document.querySelectorAll('.dyn-node-name').forEach(el => { el.textContent = nameVal; });

            const codeYaml = document.getElementById('code-yaml');
            if (codeYaml) {
                codeYaml.textContent = codeYaml.textContent
                    .split(currentScriptDest + ':/data/dest').join(destVal + ':/data/dest')
                    .split(currentScriptMount + ':/data/source:ro').join(mountVal + ':/data/source:ro')
                    .split(currentScriptPort + ':9898').join(portVal + ':9898');
            }
            const codeStartup = document.getElementById('code-startup');
            if (codeStartup) {
                codeStartup.textContent = codeStartup.textContent
                    .split('sudo mkdir -p ' + currentScriptDest).join('sudo mkdir -p ' + destVal)
                    .split(currentScriptMount + '/').join(mountVal + '/');
            }
            const codeShutdown = document.getElementById('code-shutdown');
            if (codeShutdown) {
                codeShutdown.textContent = codeShutdown.textContent
                    .split(currentScriptMount + '/').join(mountVal + '/');
            }
            currentScriptMount = mountVal;
            currentScriptDest = destVal;
            currentScriptPort = portVal;
        }

        function autoSaveGlobals() {
            syncDynamicPaths();
            const gForm = document.getElementById('globalForm');
            if (gForm) {
                fetch('/update_globals', {
                    method: 'POST',
                    body: new FormData(gForm),
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
            }
        }

        function attachGlobals(targetForm) {
            ['ext_port', 'global_host_mount', 'global_host_dest', 'tz'].forEach(key => {
                const src = document.querySelector('#globalForm [name="' + key + '"]');
                if (!src) return;
                let hidden = targetForm.querySelector('input[type="hidden"][name="' + key + '"]');
                if (!hidden) {
                    hidden = document.createElement('input');
                    hidden.type = 'hidden';
                    hidden.name = key;
                    targetForm.appendChild(hidden);
                }
                hidden.value = src.value;
            });
        }

        function openExampleModal() {
            syncDynamicPaths();
            document.getElementById('exampleModal').classList.add('active');
        }
        function closeExampleModal() {
            document.getElementById('exampleModal').classList.remove('active');
        }
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeExampleModal();
        });

        function openTab(name, btn) {
            syncDynamicPaths();
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
            syncDynamicPaths();
            
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
            syncDynamicPaths();
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
        syncDynamicPaths();
    </script>
</body>
</html>
"""

def persist_globals_from_form():
    if 'global_host_mount' not in request.form and 'global_host_dest' not in request.form:
        return
    host_mount = (request.form.get('global_host_mount') or '/mnt/source').strip().rstrip('/') or '/'
    host_dest = (request.form.get('global_host_dest') or '/mnt/dest').strip().rstrip('/') or '/'
    ext_port = (request.form.get('ext_port') or '9898').strip()
    tz_val = request.form.get('tz', '').strip()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE settings SET value=? WHERE key='ext_port'", (ext_port,))
        conn.execute("UPDATE settings SET value=? WHERE key='global_host_mount'", (host_mount,))
        conn.execute("UPDATE settings SET value=? WHERE key='global_host_dest'", (host_dest,))
        conn.execute("UPDATE settings SET value=? WHERE key='tz'", (tz_val,))

@app.route('/')
def index():
    lang = get_locale(); t = TRANSLATIONS.get(lang, TRANSLATIONS['zh'])
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        servers = [dict(r) for r in conn.execute("SELECT * FROM servers ORDER BY id DESC")]
        ext_port = conn.execute("SELECT value FROM settings WHERE key='ext_port'").fetchone()['value']
        global_mount = conn.execute("SELECT value FROM settings WHERE key='global_host_mount'").fetchone()['value']
        dest_setting = conn.execute("SELECT value FROM settings WHERE key='global_host_dest'").fetchone()
        global_dest = dest_setting['value'] if dest_setting else '/mnt/dest'
        tz_setting = conn.execute("SELECT value FROM settings WHERE key='tz'").fetchone()
        tz_val = tz_setting['value'] if tz_setting else ""
    
    def read_f(p): return open(p, 'r', encoding='utf-8').read() if os.path.exists(p) else ""
    return render_template_string(HTML_TEMPLATE, servers=servers, lang=lang, t=t, 
                                  ext_port=ext_port, global_host_mount=global_mount, global_host_dest=global_dest, tz=tz_val,
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
    persist_globals_from_form()
    sync_db_to_files()
    flash(t['flash_sync_ok'])
    return redirect('/')

@app.route('/update_globals', methods=['POST'])
def update_globals():
    t = TRANSLATIONS.get(get_locale(), TRANSLATIONS['zh'])
    persist_globals_from_form()
    sync_db_to_files()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return ('', 204)
    flash(t['flash_global_db_only'])
    return redirect('/')

@app.route('/save', methods=['POST'])
def save():
    t = TRANSLATIONS.get(get_locale(), TRANSLATIONS['zh'])
    persist_globals_from_form()
    port_val = request.form.get('port')
    
    data = {
        'id': request.form.get('id'), 'proto': request.form.get('proto'),
        'name': request.form.get('name').strip(), 'description': request.form.get('description'),
        'server_ip': request.form.get('server_ip', ''), 'remote_path': request.form.get('remote_path', ''),
        'username': request.form.get('username', ''), 'password': request.form.get('password', ''),
        'rclone_type': request.form.get('rclone_type', ''), 'rclone_args': request.form.get('rclone_args', ''),
        'port': int(port_val) if port_val and port_val.isdigit() else 0
    }
    
    saved_ok = False
    is_update = bool(data['id'])
    with sqlite3.connect(DB_PATH) as conn:
        try:
            if is_update:
                conn.execute("UPDATE servers SET proto=:proto, name=:name, description=:description, server_ip=:server_ip, remote_path=:remote_path, username=:username, password=:password, rclone_type=:rclone_type, rclone_args=:rclone_args, port=:port WHERE id=:id", data)
            else:
                conn.execute("INSERT INTO servers (proto, name, description, server_ip, remote_path, username, password, rclone_type, rclone_args, port) VALUES (:proto, :name, :description, :server_ip, :remote_path, :username, :password, :rclone_type, :rclone_args, :port)", data)
            saved_ok = True
        except sqlite3.IntegrityError:
            flash(t['flash_name_err'].format(name=data['name']), 'error')
            
    if saved_ok:
        sync_db_to_files()
        if is_update:
            flash(t['flash_update_db_only'].format(name=data['name']))
        else:
            flash(t['flash_add_ok'].format(name=data['name']))
            
    return redirect('/')

@app.route('/delete/<int:record_id>', methods=['POST'])
def delete(record_id):
    t = TRANSLATIONS.get(get_locale(), TRANSLATIONS['zh'])
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM servers WHERE id=?", (record_id,))
        
    sync_db_to_files()
    flash(t['flash_del_db_only'])
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)