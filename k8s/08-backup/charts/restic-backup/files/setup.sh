#!/bin/bash -xe
apt update && apt install -y rclone restic ca-certificates curl jq
curl -s https://raw.githubusercontent.com/fabianonline/telegram.sh/master/telegram > /usr/local/bin/telegram
chmod +x /usr/local/bin/telegram