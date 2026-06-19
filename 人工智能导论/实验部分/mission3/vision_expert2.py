import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from ultralytics import YOLO

class VisionExpertSystem(QWidget):
    def __init__(self):
        super().__init__()
        # 模拟加载的 JSON 规则库
        self.rules = [
            {"id": "R1", "premise": ["毛发", "产奶"], "conclusion": "哺乳动物"},
            {"id": "R2", "premise": ["哺乳动物", "食肉动物", "黄褐色", "斑点"], "conclusion": "虎"}
        ]
        try:
            self.model = YOLO('yolov8n.pt')  # 尝试加载 YOLO
        except:
            self.model = None
            
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("专家系统：特征逻辑与视觉感知一体化平台")
        main_layout = QHBoxLayout()
        
        # 1. 左侧：手动特征选择区域
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("手动事实输入 (特征选择):"))
        self.checkboxes = {}
        features = ["毛发", "产奶", "食肉动物", "黄褐色", "斑点"]
        for f in features:
            cb = QCheckBox(f)
            self.checkboxes[f] = cb
            left_panel.addWidget(cb)
            
        self.btn_infer = QPushButton("触发逻辑推理")
        self.btn_infer.clicked.connect(self.manual_inference)
        left_panel.addWidget(self.btn_infer)
        
        # 2. 顶部：YOLO 感知按钮
        self.btn_yolo = QPushButton("启用 YOLO 视觉感知")
        self.btn_yolo.clicked.connect(self.yolo_inference)
        left_panel.addWidget(self.btn_yolo)
        
        # 3. 右侧：带解释功能的推理记录窗
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("解释机构 (证据链推理过程):"))
        self.log = QTextEdit()
        right_panel.addWidget(self.log)
        
        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)
        self.setLayout(main_layout)

    def manual_inference(self):
        facts = {f for f, cb in self.checkboxes.items() if cb.isChecked()}
        self.run_engine(facts, "手动勾选")

    def yolo_inference(self):
        if not self.model:
            QMessageBox.warning(self, "错误", "YOLO 模型未加载！")
            return
        # 这里演示 YOLO 识别逻辑
        # detected_facts = ... (从 YOLO 结果解析)
        detected_facts = {"毛发", "产奶"} # 模拟 YOLO 结果
        self.run_engine(detected_facts, "YOLO 视觉感知")

    def run_engine(self, facts, source):
        self.log.append(f"\n--- 推理启动 (来源: {source}) ---")
        self.log.append(f"当前事实库: {facts}")
        
        # 正向推理引擎实现 (含解释说明)
        changed = True
        while changed:
            changed = False
            for r in self.rules:
                if set(r['premise']).issubset(facts) and r['conclusion'] not in facts:
                    facts.add(r['conclusion'])
                    self.log.append(f"【解释】规则 {r['id']} 被激活：{r['premise']} -> 推出 '{r['conclusion']}'")
                    changed = True
        self.log.append(f"最终判定: {facts}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = VisionExpertSystem()
    ex.show()
    sys.exit(app.exec_())