import os
import django
import time
import requests
import logging
from datetime import datetime

# ========== Django 初始化 ==========
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_refrigerator_v2.settings')
django.setup()

from monitoring.models import Item  # 确保模型路径正确

# ========== 树莓派 Flask 接口 ==========
FLASK_URL = "http://10.147.18.220:5005/receive"  # 你的树莓派 Flask IP + 端口


def send_to_raspberry(data):
    """发送控制信号到树莓派"""
    try:
        response = requests.post(FLASK_URL, json=data, timeout=3)
        response.raise_for_status()  # 若返回非 200，将触发异常
        resp_json = response.json()
        logging.info(f"✅ 树莓派响应: {resp_json}")
        print("✅ 树莓派响应:", resp_json)
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ 发送失败: {e}")
        print("❌ 发送失败:", e)


def check_and_control_fans():
    """检查数据库状态并决定是否开关风扇"""
    try:
        item_list = Item.objects.all()
        has_items = item_list.exists()
    except Exception as e:
        logging.error(f"⚠️ 数据库访问失败: {e}")
        print("⚠️ 数据库访问失败:", e)
        return

    # 判断逻辑
    if has_items:
        fan_1 = False
        fan_2 = False
        state = "检测到记录 -> 关闭风扇"
    else:
        fan_2 = False
        fan_1 = False
        state = "无记录 -> 打开风扇"

    data = {"fan_1": fan_1, "fan_2": fan_2}

    send_to_raspberry(data)


def main():
    """主循环，每 5 秒检测一次"""
    print("🌀 启动定时任务，每 5 秒检测一次...")
    logging.info("=== 风扇自动控制任务启动 ===")

    while True:
        check_and_control_fans()
        time.sleep(5)  # 间隔 5 秒


if __name__ == "__main__":
    main()
