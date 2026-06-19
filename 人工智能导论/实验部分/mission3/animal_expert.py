import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QCheckBox, QPushButton, QTextEdit, 
                             QLabel, QGroupBox, QMessageBox)
from PyQt5.QtGui import QFont

# ==========================================
# 1. 定义知识库 (规则库)
# 格式: ( {前提条件集合}, "结论" )
# ==========================================
RULES = [
    # 类别判定规则
    ({"有毛发"}, "哺乳动物"),
    ({"产奶"}, "哺乳动物"),
    ({"有羽毛"}, "鸟类"),
    ({"会飞", "下蛋"}, "鸟类"),
    ({"吃肉"}, "食肉动物"),
    ({"有犬齿", "有爪", "眼盯前方"}, "食肉动物"),
    ({"哺乳动物", "有蹄"}, "有蹄类动物"),
    ({"哺乳动物", "反刍"}, "有蹄类动物"),
    
    # 最终动物判定规则
    ({"哺乳动物", "食肉动物", "黄褐色", "暗斑点"}, "金钱豹"),
    ({"哺乳动物", "食肉动物", "黄褐色", "黑色条纹"}, "虎"),
    ({"有蹄类动物", "长脖子", "长腿", "暗斑点"}, "长颈鹿"),
    ({"有蹄类动物", "黑色条纹"}, "斑马"),
    ({"鸟类", "长脖子", "长腿", "不会飞", "黑白二色"}, "鸵鸟"),
    ({"鸟类", "会游泳", "不会飞", "黑白二色"}, "企鹅"),
    ({"鸟类", "善飞"}, "信天翁")
]

# 定义中间结论和最终结论类别，用于从UI选项中过滤掉它们
INTERMEDIATES = {"哺乳动物", "鸟类", "食肉动物", "有蹄类动物"}
TARGETS = {"虎", "金钱豹", "斑马", "长颈鹿", "鸵鸟", "企鹅", "信天翁"}

class AnimalExpertSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.checkboxes = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('产生式动物识别专家系统')
        self.resize(700, 500)
        
        main_layout = QHBoxLayout()
        
        # --- 左侧：特征选择区 ---
        left_layout = QVBoxLayout()
        features_group = QGroupBox("请选择观察到的动物特征:")
        features_group.setFont(QFont("Arial", 10, QFont.Bold))
        grid_layout = QGridLayout()
        
        # 动态提取基础特征（排除中间结论和最终结论）
        all_conditions = set()
        for conditions, _ in RULES:
            all_conditions.update(conditions)
        base_features = sorted(list(all_conditions - INTERMEDIATES - TARGETS))
        
        # 布局复选框
        row, col = 0, 0
        for feature in base_features:
            cb = QCheckBox(feature)
            cb.setFont(QFont("Arial", 10))
            self.checkboxes.append(cb)
            grid_layout.addWidget(cb, row, col)
            col += 1
            if col > 1:  # 每行放2个复选框
                col = 0
                row += 1
                
        features_group.setLayout(grid_layout)
        left_layout.addWidget(features_group)
        
        # 按钮区
        btn_layout = QHBoxLayout()
        self.infer_btn = QPushButton('开始推理')
        self.infer_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.infer_btn.clicked.connect(self.run_inference)
        
        self.reset_btn = QPushButton('重置特征')
        self.reset_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px;")
        self.reset_btn.clicked.connect(self.reset_features)
        
        btn_layout.addWidget(self.infer_btn)
        btn_layout.addWidget(self.reset_btn)
        left_layout.addLayout(btn_layout)
        
        # --- 右侧：推理过程展示区 ---
        right_layout = QVBoxLayout()
        log_label = QLabel("推理过程与结果:")
        log_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Consolas", 10))
        self.log_area.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc;")
        
        right_layout.addWidget(log_label)
        right_layout.addWidget(self.log_area)
        
        # 添加至主布局
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        self.setLayout(main_layout)

    def run_inference(self):
        self.log_area.clear()
        
        # 1. 收集事实库 (Working Memory)
        facts = set()
        for cb in self.checkboxes:
            if cb.isChecked():
                facts.add(cb.text())
                
        if not facts:
            QMessageBox.warning(self, "提示", "请至少选择一个特征！")
            return
            
        self.log_area.append("【初始事实库】: " + ", ".join(facts) + "\n")
        self.log_area.append("【开始正向推理】...")
        
        # 2. 数据驱动推理引擎
        inferred = True
        step = 1
        found_target = None
        
        while inferred:
            inferred = False
            for conditions, conclusion in RULES:
                # 如果条件是当前事实的子集，且结论还不在事实库中
                if conditions.issubset(facts) and conclusion not in facts:
                    facts.add(conclusion)
                    self.log_area.append(f"-> 步骤 {step}: 触发规则 IF {conditions} THEN {conclusion}")
                    self.log_area.append(f"   (将 '{conclusion}' 加入事实库)")
                    inferred = True
                    step += 1
                    
                    # 检查是否推理出了最终的七种动物之一
                    if conclusion in TARGETS:
                        found_target = conclusion
            
            # 如果已经找到目标动物，提前结束推理
            if found_target:
                break
                
        # 3. 输出结果
        self.log_area.append("\n" + "="*30)
        if found_target:
            self.log_area.append(f"💡 【推理成功】: 识别出的动物是 ---> **{found_target}** <---")
        else:
            self.log_area.append("❓ 【推理失败】: 根据当前特征无法识别出具体的动物。")
            self.log_area.append("    当前最终事实库包含: " + ", ".join(facts))

    def reset_features(self):
        for cb in self.checkboxes:
            cb.setChecked(False)
        self.log_area.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 设置全局字体大小，适应现代高分屏笔记本
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    
    ex = AnimalExpertSystem()
    ex.show()
    sys.exit(app.exec_())