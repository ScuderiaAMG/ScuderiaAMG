"""
main.py

程序入口文件。
负责初始化应用，显示欢迎动画，启动主循环（登录/注册 -> 主功能 -> 模拟 -> 结束动画）。
"""
import sys
import os
# 将项目根目录添加到 Python 路径，以便导入其他模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.screens.welcome_screen import show_welcome_animation # 导入欢迎动画函数
from ui.screens.login_screen import show_login_screen       # 导入登录界面函数
from ui.screens.register_screen import show_register_screen # 导入注册界面函数
from ui.screens.simulation_screen import show_simulation    # 导入模拟主界面函数
from ui.screens.goodbye_screen import show_goodbye_animation # 导入结束动画函数
from utils.logger import logger                             # 导入日志记录器

# --- 程序状态管理 ---
class AppState:
    """简单的状态管理类，用于跟踪当前用户和程序流程。"""
    def __init__(self):
        self.current_user = None

    def set_user(self, user):
        self.current_user = user

    def get_user(self):
        return self.current_user

    def clear_user(self):
        self.current_user = None

app_state = AppState()

def main():
    """
    程序主入口函数。
    """
    logger.info("=== 程序启动 ===")
    try:
        # 1. 显示开机欢迎动画
        logger.info("显示欢迎动画...")
        show_welcome_animation()

        # 2. 登录/注册循环
        logger.info("启动登录/注册流程...")
        user_authenticated = False
        while not user_authenticated:
            # 询问用户是登录还是注册
            choice = input("请选择操作: (L)ogin 或 (R)egister (输入 'Q' 退出): ").strip().upper()
            if choice == 'L':
                user = show_login_screen()
                if user:
                    app_state.set_user(user)
                    user_authenticated = True
                    logger.info(f"用户 {user.username} 登录成功。")
                else:
                    print("登录失败，请重试。")
                    logger.warning("登录失败。")
            elif choice == 'R':
                success = show_register_screen()
                if success:
                    print("注册成功，请登录。")
                    logger.info("新用户注册成功。")
                else:
                    print("注册失败。")
                    logger.warning("新用户注册失败。")
            elif choice == 'Q':
                logger.info("用户选择退出，程序结束。")
                return # 直接退出程序
            else:
                print("无效输入，请输入 'L', 'R' 或 'Q'。")

        # 3. 用户认证成功，进入主功能或模拟
        logger.info(f"用户 {app_state.get_user().username} 已认证，进入主功能...")
        # 这里可以跳转到农田创建、无人机管理、农药配置等页面
        # 或者直接进入模拟页面
        # 为了简化，这里直接进入模拟
        show_simulation(app_state.get_user())

        # 4. 模拟结束，显示结束动画
        logger.info("模拟结束，显示结束动画...")
        show_goodbye_animation()

    except KeyboardInterrupt:
        logger.info("程序被用户中断 (Ctrl+C)。")
        print("\n程序被用户中断。")
    except Exception as e:
        logger.critical(f"程序发生未处理的异常: {e}", exc_info=True)
        print(f"程序发生严重错误: {e}")
    finally:
        app_state.clear_user() # 清理用户状态
        logger.info("=== 程序结束 ===")

if __name__ == "__main__":
    main()