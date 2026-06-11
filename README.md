### 產生 Backrest yaml 檔，及啟動腳本(先自動掛載 cifs、nfs 與 sftp 後，再開啟 Backrest 容器)

#### prerequisites，先決條件，請參考    
https://github.com/WilliamFromTW/backrest_docker_yaml_generator/blob/main/(ubuntu)docker_restic.txt


#### ubuntu 
```
mkdir -p /root/backup
cd /root/backup
python3 -m venv myenv
source myenv/bin/activate
pip install flask ruamel.yaml

--------------------------------------------------------------
# setup source directory cifs(smb)，nfs 
python app.py
chrome browser： http://ip:5000
# auto generate shell script to mount source and Backrest docker
docker-compose/start.sh
docker-compose/shutdown.sh
--------------------------------------------------------------

--------------------------------------------------------------
# mount source then launch Backrest docker container
cd docker-compose 
./startup.sh
# setup restic repository and backup plan
http://ip:9898
--------------------------------------------------------------
```

