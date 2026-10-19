**English** | [繁體中文](./README.zh-TW.md)

### Generate Backrest `docker-compose.yml` & Mount Scripts (Auto-mount CIFS/SMB, NFS & Rclone/SFTP before starting the Backrest container)

#### Prerequisites
Please refer to:
- [English Guide: `(ubuntu)docker_restic.en.txt`](https://github.com/WilliamFromTW/backrest_docker_yaml_generator/blob/main/(ubuntu)docker_restic.en.txt)
- [繁體中文說明：`(ubuntu)docker_restic.txt`](https://github.com/WilliamFromTW/backrest_docker_yaml_generator/blob/main/(ubuntu)docker_restic.txt)

#### Ubuntu Usage
```bash
mkdir -p /root/backup
cd /root/backup
python3 -m venv myenv
source myenv/bin/activate
pip install flask ruamel.yaml

--------------------------------------------------------------
# 1. Start the Web UI to configure source mounts (SMB/CIFS, NFS, Rclone/SFTP)
#    and host source/destination directories (default: /mnt/source and /mnt/dest)
python app.py
# Open in Chrome browser: http://ip:5000

# The following files are automatically generated under docker-compose/:
# - docker-compose/docker-compose.yml
# - docker-compose/startup.sh
# - docker-compose/shutdown.sh
# - docker-compose/rclone.conf
--------------------------------------------------------------

--------------------------------------------------------------
# 2. Mount remote sources and launch the Backrest Docker container
cd docker-compose
./startup.sh

# 3. Configure Restic repository and backup plans in Backrest WebUI
# Open in browser: http://ip:9898
# IMPORTANT (Ref: https://github.com/garethgeorge/backrest):
# Inside Backrest (http://ip:9898), always use container paths (/data/source and /data/dest)
# instead of host paths (/mnt/source and /mnt/dest):
# - Backup source (Plan -> Paths to backup): /data/source/<subfolder_name>
# - Backup destination / Restore path (Repo / Restore): /data/dest/<subfolder_name>
--------------------------------------------------------------
```
