import sys
import os
import random
import requests
import json
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

# 【重要提示】本地运行时，请务必取消下面这行的注释，确保自启时路径正确
# os.chdir(r"D:\Applications\movingclaude")

class DeepSeekWorker(QThread):
    # 定义信号，用于将网络请求的结果异步传回主线程
    result_ready = pyqtSignal(str)

    def __init__(self, file_content, question, api_key):
        super().__init__()
        self.file_content = file_content
        self.question = question
        self.api_key = api_key

    def run(self):
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # ====== 核心配置：启动时默认调用指定的旗舰级 Pro 模型 ======
        target_model = "deepseek-v4-pro" 
        
        payload = {
            "model": target_model,
            "messages": [
                {
                    "role": "system", 
                    "content": "你是一个顶级的桌面代码与学术助手（Opus级大脑）。用户会为你提供文件内容，请进行深度、严谨、多角度的专业分析，并精准回答用户的提问。"
                },
                {
                    "role": "user", 
                    "content": f"【核心上下文文件】\n```\n{self.file_content}\n```\n\n【用户提问】\n{self.question}"
                }
            ],
            "temperature": 0.2, # 降低随机性，使其输出更符合 Pro 模型的严谨作风
            "stream": False
        }
        
        try:
            # Pro模型推理时间较长，超时时间设置为 120 秒
            response = requests.post(url, headers=headers, json=payload, timeout=120) 
            response.raise_for_status()  
            result = response.json()
            
            # 提取标准回答
            answer = result["choices"][0]["message"]["content"]
            
            # ====== 针对 Pro 模型的思维链 (Reasoning) 解析 ======
            message_data = result["choices"][0]["message"]
            think_process = message_data.get("reasoning_content") or message_data.get("reasoning")
            
            if think_process:
                answer = f"🧠【DeepSeek Pro 深度思考过程】\n{think_process}\n\n========================================\n\n🎯【核心分析解答】\n{answer}"
                    
            self.result_ready.emit(answer)
            
        except requests.exceptions.Timeout:
            self.result_ready.emit("⚠️ DeepSeek Pro 模型深度思考超时了，请检查网络或稍后重试。")
        except requests.exceptions.RequestException as e:
            self.result_ready.emit(f"❌ API 调用发生网络错误: {str(e)}")
        except Exception as e:
            self.result_ready.emit(f"❌ 运行异常: {str(e)}")


class ClaudePet(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_movement()

    def init_ui(self):
        # 永久置顶、无边框、不在任务栏显示 (Tool属性)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAcceptDrops(True) # 开启文件拖放

        self.image_label = QLabel(self)
        self.resize(120, 120)

        # ====== 预加载小怪兽的各种状态皮肤 ======
        self.sprites = {
            "idle": ["idle.png"],
            "left": ["left_1.png", "left_2.png"],
            "right": ["right_1.png", "right_2.png"],
            "up": ["up_1.png", "up_2.png"],
            "down": ["down_1.png", "down_2.png"]
        }
        self.current_state = "idle"
        self.frame_index = 0
        self.update_sprite() # 加载初始静止状态

        # ====== “思考中...” UI 提示标签 ======
        self.thinking_label = QLabel("⚡ Pro模型思考中...", self)
        self.thinking_label.setStyleSheet("""
            background-color: rgba(24, 144, 255, 230); /* 科技蓝，代表 Pro 级运算 */
            color: #ffffff;
            font-family: 'Microsoft YaHei', sans-serif;
            font-size: 9pt;
            font-weight: bold;
            border: 1px solid #1890ff;
            border-radius: 6px;
            padding: 4px;
        """)
        self.thinking_label.setAlignment(Qt.AlignCenter)
        self.thinking_label.setGeometry(0, 0, self.width(), 30)
        self.thinking_label.hide()

        self.is_dragging = False
        self.drag_offset = QPoint()
        self.show()

    def init_movement(self):
        # 1. 坐标平移动画
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(2500)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.finished.connect(self.set_idle_state)

        # 2. 漫步决策定时器：每 6 秒决定一次去哪
        self.walk_timer = QTimer(self)
        self.walk_timer.timeout.connect(self.random_move)
        self.walk_timer.start(6000)

        # 3. 肢体摆动定时器：每 200 毫秒刷新一次动作帧
        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self.next_frame)
        self.frame_timer.start(200)

    def update_sprite(self):
        """根据当前状态和帧序列更新外观"""
        file_list = self.sprites.get(self.current_state, ["idle.png"])
        if self.frame_index >= len(file_list):
            self.frame_index = 0
        
        file_name = file_list[self.frame_index]
        
        if os.path.exists(file_name):
            pixmap = QPixmap(file_name).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText(f"缺 {file_name}")
            self.image_label.setStyleSheet("background-color: white; border-radius: 10px; font-size: 8pt; text-align: center;")

    def next_frame(self):
        """让小怪兽的肢体在运动状态下动起来"""
        if self.current_state == "idle":
            return
        self.frame_index = (self.frame_index + 1) % len(self.sprites[self.current_state])
        self.update_sprite()

    def set_idle_state(self):
        """动画结束，恢复原地呆萌状态"""
        self.current_state = "idle"
        self.frame_index = 0
        self.update_sprite()

    def random_move(self):
        if self.is_dragging: 
            return
        
        screen_geo = QApplication.desktop().screenGeometry()
        cur_x, cur_y = self.x(), self.y()
        
        new_x = cur_x + random.randint(-300, 300)
        new_y = cur_y + random.randint(-300, 300)

        new_x = max(0, min(new_x, screen_geo.width() - self.width()))
        new_y = max(0, min(new_y, screen_geo.height() - self.height()))

        # 计算位移方向，改变面朝向
        dx = new_x - cur_x
        dy = new_y - cur_y

        if abs(dx) > abs(dy):
            self.current_state = "right" if dx > 0 else "left"
        else:
            self.current_state = "down" if dy > 0 else "up"

        self.frame_index = 0
        self.update_sprite()

        self.anim.setEndValue(QPoint(new_x, new_y))
        self.anim.start()

    # ====== 鼠标交互 ======
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_offset = event.globalPos() - self.pos()
            self.anim.stop() 
            self.set_idle_state() # 抓起时变成正面
            event.accept()

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.is_dragging:
            self.move(event.globalPos() - self.drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    # ====== 文件拖放与深度解析 ======
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.analyze_file(file_path)

    def analyze_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            QMessageBox.information(self, "读取成功", f"文件已成功读入（共 {len(content)} 字符）。\n小怪兽正在等待你的 Opus 级提问...")
            self.ask_question(content)
        except UnicodeDecodeError:
            QMessageBox.warning(self, "解析失败", "只能读取纯文本格式文件（如 .py, .txt, .json, .md, .cpp 等）！")
        except Exception as e:
            QMessageBox.critical(self, "发生错误", f"无法读取文件: {str(e)}")

    def ask_question(self, content):
        question, ok = QInputDialog.getText(self, 'Opus级深度提问', '请输入你想让 Pro 模型分析的内容：')
        if ok and question:
            self.thinking_label.show()
            
            # 【填写你的 API KEY】
            api_key = "YOUR_DEEPSEEK_API_KEY" 
            
            self.worker = DeepSeekWorker(content, question, api_key)
            self.worker.result_ready.connect(self.on_analysis_finished)
            self.worker.start()

    def on_analysis_finished(self, response):
        self.thinking_label.hide()
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("DeepSeek Pro 分析结果")
        msg_box.setText(response)
        msg_box.resize(600, 400) # 给 Pro 模型的长篇大论留出足够显示空间
        msg_box.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = ClaudePet()
    sys.exit(app.exec_())