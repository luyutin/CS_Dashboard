import os
import streamlit.web.cli as stcli
import sys

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    sys.argv = [
        "streamlit",
        "run",
        "main.py",
        "--global.developmentMode=false"
    ]

    # 執行 streamlit 並且在關閉後退出
    sys.exit(stcli.main())