import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from ultralytics import YOLO

# 1. 产生式推理引擎类
class ReasoningEngine:
    def __init__(self, rules):
        self.rules = rules

    def infer(self, initial_facts):
        facts = set(initial_facts)
        reasoning_chain = []
        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                if set(rule['premise']).issubset(facts) and rule['conclusion'] not in facts:
                    facts.add(rule['conclusion'])
                    reasoning_chain.append(f"触发[{rule['id']}]: {rule['premise']} -> {rule['conclusion']}")
                    changed = True
        return facts, reasoning_chain

# 2. GUI 主界面
class VisionExpertSystem(QWidget):
    def __init__(self):
        super().__init__()
        # 预设规则 (实际可从 JSON 读取)
        self.rules = [
            {"id": "R1", "premise": ["毛发", "产奶"], "conclusion": "哺乳动物"},
            {"id": "R2", "premise": ["哺乳动物", "食肉动物", "黄褐色", "黑色条纹"], "conclusion": "虎"}
        ]
        self.engine = ReasoningEngine(self.rules)
        self.model = YOLO('yolov8n.pt')  # 加载轻量级YOLO模型
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("视觉感知型动物识别系统")
        layout = QVBoxLayout()
        
        self.btn_load = QPushButton("载入图片进行感知与推理")
        self.btn_load.clicked.connect(self.process_image)
        self.log = QTextEdit()
        
        layout.addWidget(self.btn_load)
        layout.addWidget(QLabel("推理过程与证据链:"))
        layout.addWidget(self.log)
        self.setLayout(layout)

    def process_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, "选择图片")
        if not fname: return
        
        # YOLO 感知
        results = self.model(fname)
        detected_labels = [self.model.names[int(box.cls)] for box in results[0].boxes]
        self.log.append(f"YOLO 感知到事实: {detected_labels}")
        
        # 逻辑推理
        final_facts, chain = self.engine.infer(detected_labels)
        for step in chain: self.log.append(step)
        self.log.append(f"最终判定结论: {final_facts}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = VisionExpertSystem()
    ex.show()
    sys.exit(app.exec_())