import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QCheckBox, QPushButton, QTextEdit, 
                             QLabel, QGroupBox, QMessageBox, QScrollArea)
from PyQt5.QtGui import QFont

# 知识表示层
class Rule:
    def __init__(self, rule_id, premise, conclusion, priority=1):
        self.rule_id = rule_id
        self.premise = set(premise)  # 前提转成 set，方便后面做子集判断
        self.conclusion = conclusion
        self.priority = priority     # 数字越小 = 越基础的规则 = 越优先触发

class KnowledgeBase:
    def __init__(self, json_path):
        self.rules = []
        self.targets = set()
        self.load_from_json(json_path)

    # def load_from_json(self, json_path):
    #     """旧版加载器（保留以备对比）"""
    #     if not os.path.exists(json_path):
    #         return
    #     try:
    #         with open(json_path, 'r', encoding='utf-8') as f:
    #             data = json.load(f)
    #             self.targets = set(data.get("targets", []))
    #             for r in data.get("rules", []):
    #                 rule = Rule(r["id"], r["premise"], r["conclusion"], r.get("priority", 1))
    #                 self.rules.append(rule)
    #     except Exception as e:
    #         print(f"知识库加载失败: {e}")
    def load_from_json(self, json_path):
        if not os.path.exists(json_path):
            return
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # 1. 加载全部规则
                for r in data.get("rules", []):
                    rule = Rule(r["id"], r["premise"], r["conclusion"], r.get("priority", 1))
                    self.rules.append(rule)

                #自动推导最终目标（Terminal Nodes）
                # 如果 JSON 显式配了 targets 就用，否则扫描规则自动算
                if "targets" in data:
                    self.targets = set(data["targets"])
                else:
                    all_premises = set()
                    all_conclusions = set()
                    for r in self.rules:
                        all_premises.update(r.premise)
                        all_conclusions.add(r.conclusion)
                    # 出现在结论里但从未作为前提的 → 即最终目标动物
                    self.targets = all_conclusions - all_premises

        except Exception as e:
            print(f"知识库加载失败: {e}")

    def get_all_premises(self):

        all_conditions = set()
        for rule in self.rules:
            all_conditions.update(rule.premise)
        # 排除中间结论和目标，只留用户能直接观察的特征
        conclusions = {r.conclusion for r in self.rules}
        return sorted(list(all_conditions - conclusions - self.targets))

# 推理引擎 —— 正向链接 + 冲突消解 + 解释日志
class InferenceEngine:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.explanation_log = []  # 记录每步推理

    def forward_chaining(self, initial_facts):
        working_memory = set(initial_facts)
        self.explanation_log.clear()
        self.explanation_log.append(f"【初始事实库】: {', '.join(working_memory)}\n")

        inferred = True
        step = 1
        found_target = None
        used_rules = set()

        self.explanation_log.append("【开始正向推理】")

        while inferred:
            inferred = False
            conflict_set = []

            # 扫描所有未用过的规则，前提完全被满足的加入候选
            for rule in self.kb.rules:
                if rule.rule_id not in used_rules and rule.premise.issubset(working_memory):
                    conflict_set.append(rule)

            if not conflict_set:
                break

            #priority 数字越小越先触发，同 priority 下条件越多越优先
            conflict_set.sort(key=lambda r: (r.priority, -len(r.premise)))

            #执行
            selected_rule = conflict_set[0]
            used_rules.add(selected_rule.rule_id)
            working_memory.add(selected_rule.conclusion)

            log_line = (f"-> 步骤 {step}: 触发规则 [{selected_rule.rule_id}]\n"
                        f"   IF   {' AND '.join(selected_rule.premise)}\n"
                        f"   THEN {selected_rule.conclusion}\n"
                        f"   (事实库加入: '{selected_rule.conclusion}')\n")
            self.explanation_log.append(log_line)

            inferred = True
            step += 1

            if selected_rule.conclusion in self.kb.targets:
                found_target = selected_rule.conclusion
                break

        return found_target, working_memory, self.explanation_log

# PyQt5 界面 —— 动态复选框 + 推理展示 + 部分匹配推荐
class AnimalExpertSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.kb = KnowledgeBase("knowledge.json")
        self.engine = InferenceEngine(self.kb)
        self.checkboxes = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('动物识别')
        self.resize(850, 600)
        
        main_layout = QHBoxLayout()
        
        # --- 左侧：动态特征选择区 ---
        left_layout = QVBoxLayout()
        
        features_group = QGroupBox("请选择观察到的动物特征:")
        features_group.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        
        # 滚动区域：特征多了不会溢出
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        grid_layout = QGridLayout(scroll_widget)

        base_features = self.kb.get_all_premises()

        if not base_features:
            QMessageBox.critical(self, "错误", "未能加载特征，请检查 knowledge.json。")
        
        row, col = 0, 0
        for feature in base_features:
            cb = QCheckBox(feature)
            cb.setFont(QFont("Microsoft YaHei", 10))
            self.checkboxes.append(cb)
            grid_layout.addWidget(cb, row, col)
            col += 1
            if col > 1:  # 每行2列
                col = 0
                row += 1
                
        scroll.setWidget(scroll_widget)
        
        left_layout.addWidget(features_group)
        features_group.setLayout(QVBoxLayout())
        features_group.layout().addWidget(scroll)
        
        # 按钮区
        btn_layout = QHBoxLayout()
        self.infer_btn = QPushButton('开始推理')
        self.infer_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.infer_btn.clicked.connect(self.run_inference)
        
        self.reset_btn = QPushButton('重置特征')
        self.reset_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.reset_btn.clicked.connect(self.reset_features)
        
        btn_layout.addWidget(self.infer_btn)
        btn_layout.addWidget(self.reset_btn)
        left_layout.addLayout(btn_layout)
        
        # --- 右侧：推理过程展示区 ---
        right_layout = QVBoxLayout()
        log_label = QLabel("解释机构 (推理链追踪):")
        log_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Consolas", 10))
        self.log_area.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ccc; padding: 5px;")
        
        right_layout.addWidget(log_label)
        right_layout.addWidget(self.log_area)
        
        # 左右比例 1:1.5
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 3)
        self.setLayout(main_layout)

    # def run_inference(self):
    #     """旧版：仅精确匹配"""
    #     self.log_area.clear()
    #
    #     facts = [cb.text() for cb in self.checkboxes if cb.isChecked()]
    #
    #     if not facts:
    #         QMessageBox.warning(self, "提示", "请至少选择一个特征！")
    #         return
    #
    #     target, final_memory, logs = self.engine.forward_chaining(facts)
    #
    #     for line in logs:
    #         self.log_area.append(line)
    #
    #     self.log_area.append("="*40)
    #     if target:
    #         self.log_area.append(f"\n 推理成功,识别出的动物是 ---> **{target}** <---")
    #     else:
    #         self.log_area.append("\n 推理失败,知识库中没有匹配的动物。")
    #         self.log_area.append("    当前最终事实库包含: " + ", ".join(final_memory))

    def run_inference(self):
        self.log_area.clear()
        
        facts = [cb.text() for cb in self.checkboxes if cb.isChecked()]
                
        if not facts:
            QMessageBox.warning(self, "提示", "请选择一个特征")
            return
            
        target, final_memory, logs = self.engine.forward_chaining(facts)
        
        # 输出推理日志
        for line in logs:
            self.log_area.append(line)

        self.log_area.append("="*40)
        if target:
            self.log_area.append(f"\n推理成功,识别出的动物是 ---> **{target}** <---")
        else:
            # 精确匹配失败 → 计算部分匹配推荐
            candidates = []

            # 递归展开某个结论的完整特征依赖树
            def get_all_dependencies(conclusion, visited=None):
                if visited is None:
                    visited = set()
                if conclusion in visited:
                    return set()  # 防环
                visited.add(conclusion)

                deps = set()
                for r in self.engine.kb.rules:
                    if r.conclusion == conclusion:
                        deps.update(r.premise)
                        for p in r.premise:
                            deps.update(get_all_dependencies(p, visited))
                return deps

            for possible_target in self.engine.kb.targets:
                target_deps = get_all_dependencies(possible_target)
                target_deps.add(possible_target)

                intersect = target_deps.intersection(final_memory)
                if intersect:
                    candidates.append({
                        "target": possible_target,
                        "matched": intersect
                    })

            if not candidates:
                self.log_area.append("\n无法匹配,当前特征与知识库中任何动物均无交集。")
                self.log_area.append("    当前最终事实库包含: " + ", ".join(final_memory))
            else:
                self.log_area.append("\n特征不足,以下动物满足部分特征：")
                candidates.sort(key=lambda x: len(x["matched"]), reverse=True)
                for c in candidates:
                    matched_str = ", ".join(c["matched"])
                    self.log_area.append(f"候选: **{c['target']}**")
                    self.log_area.append(f"命中特征: {matched_str}")

    def reset_features(self):
        for cb in self.checkboxes:
            cb.setChecked(False)
        self.log_area.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AnimalExpertSystem()
    ex.show()
    sys.exit(app.exec_())