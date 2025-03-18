#!/usr/bin/expect
set ipv4 [exec curl -s http://100.100.100.200/latest/meta-data/eipv4]

spawn bash ./setup.sh
expect "(0,1) \[0\]:"
send "1\r"
expect "(0,1,2) \[2\]:"
send "1\r"
expect "LobeChat部署IP/域名 \[*\]:"
send "$ipv4\r"
expect "(y/n) \[y\]:"
send "y\r"

# 等待交互结束
expect eof
