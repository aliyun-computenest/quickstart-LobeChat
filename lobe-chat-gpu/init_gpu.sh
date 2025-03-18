#gpu驱动安装
#!/bin/sh
#Please input version to install
DRIVER_VERSION="550.127.08"
CUDA_VERSION="12.4.1"
CUDNN_VERSION="9.2.0.82"
IS_INSTALL_eRDMA="FALSE"
IS_INSTALL_RDMA="FALSE"
INSTALL_DIR="/root/auto_install"

#using .run to install driver and cuda 
auto_install_script="auto_install_v4.0.sh"

script_download_url=$(curl http://100.100.100.200/latest/meta-data/source-address | head -1)"/opsx/ecs/linux/binary/script/${auto_install_script}"
echo $script_download_url

rm -rf $INSTALL_DIR
mkdir -p $INSTALL_DIR 
cd $INSTALL_DIR && wget -t 10 --timeout=10 $script_download_url && bash ${INSTALL_DIR}/${auto_install_script} $DRIVER_VERSION $CUDA_VERSION $CUDNN_VERSION $IS_INSTALL_RDMA $IS_INSTALL_eRDMA
