#!/usr/bin/env python3
"""Start the local editor independently of the terminal and wait until ready."""
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
URL = 'http://127.0.0.1:8765/'


def ready():
    try:
        with urllib.request.urlopen(URL + 'api/health', timeout=1) as response:
            import json
            data = json.load(response)
            return data.get('service') == 'hn-ad-studio' and data.get('version') == 2
    except (OSError, ValueError):
        return False


def main():
    if not ready():
        logs = ROOT / 'outputs'
        logs.mkdir(exist_ok=True)
        with (logs / 'server.log').open('ab') as log:
            process = subprocess.Popen(
                [sys.executable, str(ROOT / 'server.py')],
                stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                start_new_session=True, close_fds=True,
            )
        for _ in range(50):
            if ready():
                break
            if process.poll() is not None:
                raise SystemExit('启动失败，请查看日志：' + str(logs / 'server.log'))
            time.sleep(0.1)
        else:
            raise SystemExit('服务未就绪，请查看日志：' + str(logs / 'server.log'))
    print('HN爆单出品已就绪：' + URL)
    if '--no-open' not in sys.argv:
        subprocess.run(['open', URL], check=True)


if __name__ == '__main__':
    main()
