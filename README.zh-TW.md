[English](./README.md) | **繁體中文**

### 產生 Backrest `docker-compose.yml` 檔及啟動腳本（先自動掛載 CIFS/SMB、NFS 與 Rclone/SFTP 後，再開啟 Backrest 容器）

#### 先決條件 (Prerequisites)
請參考：
- [繁體中文說明：`(ubuntu)docker_restic.txt`](https://github.com/WilliamFromTW/backrest_docker_yaml_generator/blob/main/(ubuntu)docker_restic.txt)
- [English Guide: `(ubuntu)docker_restic.en.txt`](https://github.com/WilliamFromTW/backrest_docker_yaml_generator/blob/main/(ubuntu)docker_restic.en.txt)

#### Ubuntu 操作流程
```bash
mkdir -p /root/backup
cd /root/backup
python3 -m venv myenv
source myenv/bin/activate
pip install flask ruamel.yaml

--------------------------------------------------------------
# 1. 啟動 Web 介面設定遠端來源 (SMB/CIFS、NFS、Rclone/SFTP)
#    與宿主機來源/目標目錄 (預設為 /mnt/source 與 /mnt/dest)
python app.py
# 使用 Chrome 瀏覽器開啟： http://ip:5000

# 系統會自動在 docker-compose/ 目錄下產生以下檔案：
# - docker-compose/docker-compose.yml
# - docker-compose/startup.sh
# - docker-compose/shutdown.sh
# - docker-compose/rclone.conf
--------------------------------------------------------------

--------------------------------------------------------------
# 2. 掛載遠端來源並啟動 Backrest Docker 容器
cd docker-compose
./startup.sh

# 3. 進入 Backrest 介面設定 Restic 儲存庫 (Repo) 與備份計畫 (Plan)
# 使用瀏覽器開啟： http://ip:9898
# 重要提醒 (參考官方文件: https://github.com/garethgeorge/backrest)：
# 在 Backrest (http://ip:9898) 內設定的來源與目標路徑，都必須填寫 Docker 容器內的路徑 (/data/source、/data/dest)，
# 而不是宿主機的 /mnt/source、/mnt/dest：
# - 備份來源 (Plan -> Paths to backup): /data/source/<子目錄名稱>
# - 備份目標 / 還原路徑 (Repo / Restore): /data/dest/<子目錄名稱>
--------------------------------------------------------------
```
