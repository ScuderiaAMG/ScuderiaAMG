#!/usr/bin/env python3
"""
农田无人机喷洒农药模拟系统 - 主程序入口
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import FarmDroneApp

if __name__ == "__main__":
    app = FarmDroneApp()
    app.run()