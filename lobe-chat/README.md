# 部署内容包括：
* LobeChat 数据库版本自身(使用PostgreSQL)
* 带有 PGVector 插件的 PostgreSQL 数据库
* 支持 S3 协议的对象存储服务 (使用本地部署minio)
* 受 LobeChat 支持的 SSO 登录鉴权服务 (使用本地部署casdoor  )
# 开放端口
3210、9001、8000

# 需要透露给用户的应用信息：

##  lobe-chat
* lobchatUrl: http://IPv4:3210/
* username:user
* 获取随机password:
 脚本：
cat init_data.json | jq -r '.users[] | select(.name == "user") | .password'

##  minio
* minioUrl: http://IPv4:9001/
* username:admin
* 获取随机password:
docker exec -ti lobe-minio env| awk -F '=' '/^MINIO_ROOT_PASSWORD=/ {print $2}'


## casdoor
casdoorUrl: http://IPv4:8000/
* username:admin
* 获取随机password:
cat init_data.json | jq -r '.users[] | select(.name == "admin") | .password'

