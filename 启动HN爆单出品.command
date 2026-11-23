#!/bin/zsh
cd "${0:A:h}" || exit 1
python3 start_tool.py
if [[ $? -ne 0 ]]; then
  read "reply?启动失败，请查看错误信息，按回车关闭"
fi
