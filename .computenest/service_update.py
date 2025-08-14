#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
import argparse
import sys
import logging
import time
import yaml
import os
import tempfile
import shutil
import platform
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ServiceUpdater")

# 所有支持的地域列表
ALL_ALLOWED_REGIONS = [
    "cn-hangzhou", "cn-zhengzhou", "cn-shanghai", "cn-nanjing",
    "cn-fuzhou", "cn-qingdao", "cn-beijing", "cn-zhangjiakou", 
    "cn-wulanchabu", "cn-shenzhen", "cn-heyuan", "cn-guangzhou", 
    "cn-chengdu", "cn-hongkong", "ap-southeast-1", "ap-southeast-3", 
    "ap-southeast-5", "ap-southeast-6", "ap-southeast-7", 
    "ap-northeast-1", "ap-northeast-2", "eu-central-1", "eu-west-1",
    "us-west-1", "us-east-1", "me-central-1"
]

def run_command(command):
    """执行命令并返回结果"""
    logger.info(f"执行命令: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"命令执行失败: {e}")
        logger.error(f"错误输出: {e.stderr}")
        raise

def install_aliyun_cli():
    """安装阿里云CLI"""
    logger.info("开始安装阿里云CLI...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    try:
        # 获取当前系统类型
        system = platform.system().lower()
        
        if system == 'linux':
            # 下载Linux版本的阿里云CLI
            download_url = "https://aliyuncli.alicdn.com/aliyun-cli-linux-latest-amd64.tgz"
            download_path = os.path.join(temp_dir, "aliyun-cli.tgz")
            
            # 下载文件
            run_command(f"wget -q {download_url} -O {download_path}")
            
            # 解压文件
            run_command(f"tar -xzf {download_path} -C {temp_dir}")
            
            # 移动到可执行路径
            aliyun_bin = os.path.join(temp_dir, "aliyun")
            if os.path.exists(aliyun_bin):
                dest_path = "/usr/local/bin/aliyun"
                run_command(f"sudo cp {aliyun_bin} {dest_path}")
                run_command(f"sudo chmod +x {dest_path}")
                logger.info(f"阿里云CLI已安装到 {dest_path}")
            else:
                raise Exception("未找到解压后的aliyun可执行文件")
        
        elif system == 'darwin':  # macOS
            # 下载macOS版本的阿里云CLI
            download_url = "https://aliyuncli.alicdn.com/aliyun-cli-macosx-latest-amd64.tgz"
            download_path = os.path.join(temp_dir, "aliyun-cli.tgz")
            
            # 下载文件
            run_command(f"curl -s {download_url} -o {download_path}")
            
            # 解压文件
            run_command(f"tar -xzf {download_path} -C {temp_dir}")
            
            # 移动到可执行路径
            aliyun_bin = os.path.join(temp_dir, "aliyun")
            if os.path.exists(aliyun_bin):
                dest_path = "/usr/local/bin/aliyun"
                run_command(f"sudo cp {aliyun_bin} {dest_path}")
                run_command(f"sudo chmod +x {dest_path}")
                logger.info(f"阿里云CLI已安装到 {dest_path}")
            else:
                raise Exception("未找到解压后的aliyun可执行文件")
        
        elif system == 'windows':
            # 下载Windows版本的阿里云CLI
            download_url = "https://aliyuncli.alicdn.com/aliyun-cli-windows-latest-amd64.zip"
            download_path = os.path.join(temp_dir, "aliyun-cli.zip")
            
            # 下载文件
            run_command(f"curl -s {download_url} -o {download_path}")
            
            # 解压文件
            run_command(f"powershell -Command \"Expand-Archive -Path {download_path} -DestinationPath {temp_dir}\"")
            
            # 移动到可执行路径
            aliyun_bin = os.path.join(temp_dir, "aliyun.exe")
            if os.path.exists(aliyun_bin):
                # 在Windows上，我们将其移动到当前目录，并添加到PATH
                dest_path = os.path.join(os.getcwd(), "aliyun.exe")
                shutil.copy(aliyun_bin, dest_path)
                logger.info(f"阿里云CLI已安装到 {dest_path}")
                
                # 添加到当前会话的PATH
                os.environ["PATH"] = os.getcwd() + os.pathsep + os.environ["PATH"]
            else:
                raise Exception("未找到解压后的aliyun.exe文件")
        
        else:
            raise Exception(f"不支持的操作系统: {system}")
        
        # 验证安装
        version_output = run_command("aliyun version")
        logger.info(f"阿里云CLI安装成功: {version_output.strip()}")
        return True
    
    except Exception as e:
        logger.error(f"安装阿里云CLI失败: {e}")
        return False
    
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

def configure_aliyun_cli(access_key_id, access_key_secret, region="cn-hangzhou"):
    """配置阿里云CLI"""
    logger.info("开始配置阿里云CLI...")
    
    try:
        command = (
            f"aliyun configure set "
            f"--profile AkProfile "
            f"--mode AK "
            f"--access-key-id {access_key_id} "
            f"--access-key-secret {access_key_secret} "
            f"--region {region}"
        )
        
        # 执行配置命令，但不显示敏感信息
        logger.info("执行命令: aliyun configure set --profile AkProfile --mode AK --access-key-id *** --access-key-secret *** --region cn-hangzhou")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        
        logger.info("阿里云CLI配置成功")
        return True
    
    except Exception as e:
        logger.error(f"配置阿里云CLI失败: {e}")
        return False

def read_config_yaml(file_path):
    """读取config.yaml文件并解析"""
    # 如果提供的是目录路径，则尝试查找.computenest/config.yaml
    config_path = Path(file_path)
    if config_path.is_dir():
        config_path = config_path / ".computenest" / "config.yaml"
    
    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path}")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            logger.info(f"成功读取配置文件: {config_path}")
            return config
    except Exception as e:
        logger.error(f"读取配置文件失败: {e}")
        return None

def get_allowed_regions_from_config(config):
    """从配置文件中获取AllowedRegions列表"""
    if not config or 'Service' not in config or 'DeployMetadata' not in config['Service']:
        return []
    
    deploy_metadata = config['Service']['DeployMetadata']
    
    # 尝试从SupplierDeployMetadata中获取
    if 'SupplierDeployMetadata' in deploy_metadata and 'SupplierTemplateConfigs' in deploy_metadata['SupplierDeployMetadata']:
        for config in deploy_metadata['SupplierDeployMetadata']['SupplierTemplateConfigs']:
            if 'AllowedRegions' in config:
                return config['AllowedRegions']
    
    # 尝试从TemplateConfigs中获取
    if 'TemplateConfigs' in deploy_metadata:
        for config in deploy_metadata['TemplateConfigs']:
            if 'AllowedRegions' in config:
                return config['AllowedRegions']
    
    return []

def determine_regions_to_add(config):
    """根据配置文件决定要添加的地域"""
    allowed_regions = get_allowed_regions_from_config(config)
    
    # 如果配置中的地域列表只有一个，则使用所有支持的地域
    if len(allowed_regions) <= 1:
        logger.info(f"配置中只有 {len(allowed_regions)} 个地域，将使用所有支持的地域")
        return ALL_ALLOWED_REGIONS
    
    # 否则使用配置中已有的地域
    logger.info(f"配置中已有 {len(allowed_regions)} 个地域，将使用这些地域")
    return allowed_regions

def get_service_metadata(service_id, region, service_version="draft"):
    """获取服务的DeployMetadata"""
    logger.info(f"获取服务 {service_id} 的元数据...")
    
    command = (
        f"aliyun computenestsupplier GetService "
        f"--region {region} "
        f"--RegionId '{region}' "
        f"--ServiceId '{service_id}' "
        f"--ServiceVersion {service_version}"
    )
    
    result = run_command(command)
    try:
        service_data = json.loads(result)
        deploy_metadata_str = service_data.get("DeployMetadata")
        
        if not deploy_metadata_str:
            logger.error("无法获取DeployMetadata")
            return None
        
        # 解析嵌套的JSON字符串
        deploy_metadata = json.loads(deploy_metadata_str)
        logger.info("成功获取服务元数据")
        return deploy_metadata
    except json.JSONDecodeError as e:
        logger.error(f"解析服务元数据失败: {e}")
        logger.error(f"原始响应: {result}")
        return None

def add_regions_to_metadata(deploy_metadata, new_regions):
    """向DeployMetadata中添加新的地域"""
    logger.info(f"添加新地域: {new_regions}")
    
    # 检查是否有SupplierDeployMetadata
    if "SupplierDeployMetadata" not in deploy_metadata:
        logger.error("元数据中没有SupplierDeployMetadata字段")
        return deploy_metadata
    
    # 处理SupplierTemplateConfigs中的AllowedRegions
    supplier_configs = deploy_metadata["SupplierDeployMetadata"].get("SupplierTemplateConfigs", [])
    for config in supplier_configs:
        if "AllowedRegions" in config:
            current_regions = set(config["AllowedRegions"])
            for region in new_regions:
                if region not in current_regions:
                    logger.info(f"向配置 {config.get('Name', 'unknown')} 添加地域 {region}")
                    config["AllowedRegions"].append(region)
    
    # 处理TemplateConfigs中的AllowedRegions
    template_configs = deploy_metadata.get("TemplateConfigs", [])
    for config in template_configs:
        if "AllowedRegions" in config:
            current_regions = set(config["AllowedRegions"])
            for region in new_regions:
                if region not in current_regions:
                    logger.info(f"向模板配置 {config.get('Name', 'unknown')} 添加地域 {region}")
                    config["AllowedRegions"].append(region)
    
    return deploy_metadata

def update_service(service_id, region, deploy_metadata, service_version="draft"):
    """更新服务的DeployMetadata"""
    logger.info(f"更新服务 {service_id} 的元数据...")
    
    # 将DeployMetadata转换为JSON字符串
    deploy_metadata_str = json.dumps(deploy_metadata).replace('"', '\\"')
    
    command = (
        f'aliyun computenestsupplier UpdateService '
        f'--region {region} '
        f'--RegionId \'{region}\' '
        f'--DeployMetadata \'{json.dumps(deploy_metadata)}\' '
        f'--ServiceId \'{service_id}\' '
        f'--ServiceVersion {service_version}'
    )
    
    result = run_command(command)
    try:
        update_result = json.loads(result)
        logger.info(f"服务更新结果: {update_result}")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"解析更新结果失败: {e}")
        logger.error(f"原始响应: {result}")
        return False

def pre_launch_service(service_id, region):
    """预发布服务"""
    logger.info(f"预发布服务 {service_id}...")
    
    command = (
        f"aliyun computenestsupplier PreLaunchService "
        f"--region {region} "
        f"--RegionId \'{region}\' "
        f"--ServiceId \'{service_id}\'"
    )
    
    result = run_command(command)
    try:
        pre_launch_result = json.loads(result) if result.strip() else {}
        logger.info(f"服务预发布结果: {pre_launch_result}")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"解析预发布结果失败: {e}")
        logger.error(f"原始响应: {result}")
        return False

def main():
    parser = argparse.ArgumentParser(description='更新服务地域并预发布')
    parser.add_argument('--service-id', required=True, help='服务ID')
    parser.add_argument('--region', default='cn-hangzhou', help='操作的区域')
    parser.add_argument('--version', default='draft', help='服务版本')
    parser.add_argument('--pre-launch', action='store_true', help='是否执行预发布')
    parser.add_argument('--file_path', default='.', help='配置文件路径或包含.computenest目录的路径')
    parser.add_argument('--force-all-regions', action='store_true', help='强制使用所有支持的地域，忽略配置文件')
    parser.add_argument('--access-key-id', help='阿里云访问密钥ID')
    parser.add_argument('--access-key-secret', help='阿里云访问密钥Secret')
    parser.add_argument('--skip-cli-install', action='store_true', help='跳过阿里云CLI安装')
    
    args = parser.parse_args()
    
    try:
        # 1. 安装阿里云CLI（如果需要）
        if not args.skip_cli_install:
            # 检查阿里云CLI是否已安装
            try:
                run_command("aliyun version")
                logger.info("阿里云CLI已安装，跳过安装步骤")
            except:
                logger.info("阿里云CLI未安装，开始安装...")
                if not install_aliyun_cli():
                    logger.error("安装阿里云CLI失败，退出程序")
                    return 1
        
        # 2. 配置阿里云CLI（如果提供了密钥）
        if args.access_key_id and args.access_key_secret:
            if not configure_aliyun_cli(args.access_key_id, args.access_key_secret, args.region):
                logger.error("配置阿里云CLI失败，退出程序")
                return 1
        
        # 3. 读取配置文件
        config = read_config_yaml(args.file_path)
        if not config and not args.force_all_regions:
            logger.error("读取配置文件失败且未指定强制使用所有地域，退出程序")
            return 1
        
        # 4. 确定要添加的地域
        if args.force_all_regions:
            regions_to_add = ALL_ALLOWED_REGIONS
            logger.info("强制使用所有支持的地域")
        else:
            regions_to_add = determine_regions_to_add(config)
        
        logger.info(f"将添加以下地域: {regions_to_add}")
        
        # 5. 获取服务元数据
        deploy_metadata = get_service_metadata(args.service_id, args.region, args.version)
        if not deploy_metadata:
            logger.error("获取服务元数据失败，退出程序")
            return 1
        
        # 6. 添加新地域
        updated_metadata = add_regions_to_metadata(deploy_metadata, regions_to_add)
        
        # 7. 更新服务
        update_success = update_service(args.service_id, args.region, updated_metadata, args.version)
        if not update_success:
            logger.error("更新服务失败，退出程序")
            return 1
        
        # 等待一段时间，确保更新已完成
        logger.info("等待10秒，确保更新已完成...")
        time.sleep(10)
        
        # 8. 预发布服务（如果指定了--pre-launch参数）
        if args.pre_launch:
            pre_launch_success = pre_launch_service(args.service_id, args.region)
            if not pre_launch_success:
                logger.error("预发布服务失败")
                return 1
            logger.info("服务预发布成功")
        
        logger.info("所有操作已成功完成")
        return 0
    
    except Exception as e:
        logger.exception(f"程序执行过程中出现异常: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

