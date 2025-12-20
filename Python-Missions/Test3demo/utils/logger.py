"""
utils/logger.py

设置和提供日志记录器实例。
"""
import logging
from config import LOG_FILE_PATH, LOG_LEVEL

# 配置根日志记录器
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL), # 使用 config.py 中定义的级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode='a', encoding='utf-8'), # 写入文件
        logging.StreamHandler() # 同时输出到控制台
    ]
)

# 创建一个特定的 logger 实例，方便在其他模块中使用
logger = logging.getLogger('AgriDroneSim') # 使用项目名称作为 logger 名称

if __name__ == "__main__":
    # 测试日志记录
    logger.debug("这是一个调试信息")
    logger.info("这是一个信息")
    logger.warning("这是一个警告")
    logger.error("这是一个错误")
    logger.critical("这是一个严重错误")
