### Docker 常見指令
1. docker run <image>：從映像檔建立並啟動一個新的容器。 
  功能：從映像檔建立並啟動一個新的容器
  常用參數：
    -d: 背景執行
    -p: 連接埠映射
    --name: 指定容器名稱
    範例：docker run -d -p 80:80 --name web nginx
2. docker ps：列出正在運行的容器。
    功能：列出目前正在運行的容器
    顯示資訊：
    - 容器 ID
    - 映像檔名稱
    - 建立時間
    - 狀態
    - 連接埠
    - 容器名稱
3. docker stop <container>：停止一個容器。 
    - 功能：停止指定的容器 
    - 可使用容器 ID 或容器名稱 
    - 範例：
    - `docker stop web`
    - `docker stop 1234abc`
4. docker ps -a ：列出所有容器，包含停止的容器。
    - 功能：列出所有容器（包含已停止的容器）
    - 顯示與 docker ps 相同的資訊，但包含停止狀態的容器
5. docker rm <container>：移除一個容器。
    - 功能：永久移除指定的容器
    - 注意：需要先停止容器才能移除
    - 範例：`docker rm web`
6. docker images：列出本地的所有映像檔。
    - 功能：列出本機上所有的 Docker 映像檔
    - 顯示資訊： \
    映像檔名稱 \
    標籤 \
    映像檔 ID \
    建立時間 \
    大小
7. docker rmi <image>：移除一個映像檔。
    - 功能：移除指定的映像檔
    - 注意：需要確保沒有容器使用該映像檔
    - 範例：`docker rmi nginx:latest`
8. docker pull <image>：從 Docker Hub 或其他 Docker Registry 下載一個映像檔。
    - 功能：從遠端倉庫下載映像檔
    - 預設從 Docker Hub 下載
    - 範例：`docker pull ubuntu:20.04`
9. docker build -t <image> .：從當前目錄的 Dockerfile 建立一個新的映像檔。
    - 功能：使用 Dockerfile 建立新的映像檔
    - -t: 指定映像檔名稱和標籤
.: 指定 Dockerfile 所在的目錄
    - 範例：docker build -t myapp:1.0 .
10. docker exec -it <container> bash：進入一個正在運行的容器的 bash shell。
    - 功能：以互動模式進入執行中的容器
    - -it: 互動式終端機
    - bash: 要執行的命令
    - 範例：docker exec -it web bash
11. docker run -d -p 8080:3000 <image名稱:tag> ：在背景運行