
#!/bin/sh
# alinux docker 安装
#添加Docker软件包源
sudo wget -O /etc/yum.repos.d/docker-ce.repo http://mirrors.cloud.aliyuncs.com/docker-ce/linux/centos/docker-ce.repo
sudo sed -i 's|https://mirrors.aliyun.com|http://mirrors.cloud.aliyuncs.com|g' /etc/yum.repos.d/docker-ce.repo
#Alibaba Cloud Linux3专用的dnf源兼容插件
sudo dnf -y install dnf-plugin-releasever-adapter --repo alinux3-plus
#安装Docker社区版本，容器运行时containerd.io，以及Docker构建和Compose插件
sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
#启动Docker
sudo systemctl start docker
#设置Docker守护进程在系统启动时自动启动
sudo systemctl enable docker

sudo systemctl status docker
sudo dnf install -y anolis-epao-release
sudo dnf install -y kernel-devel-$(uname -r) nvidia-driver{,-cuda}
sudo dnf install -y nvidia-container-toolkit
sudo systemctl restart docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker



yum install -y expect
docker pull lobehub/lobe-chat-database:v1.52.16
docker pull casbin/casdoor:v1.832.0
docker pull minio/minio:RELEASE.2025-02-07T23-21-09Z-cpuv1
docker pull ector:pg17
docker pull alpine:latest