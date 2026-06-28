from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


ROOT = Path(__file__).resolve().parent
DOCX = max([p for p in ROOT.iterdir() if p.suffix.lower() == ".docx"], key=lambda p: p.stat().st_mtime)


def set_run_font(run, east="宋体", west="Times New Roman", size=10.5, bold=None):
    run.font.name = west
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:eastAsia"), east)
    rfonts.set(qn("w:ascii"), west)
    rfonts.set(qn("w:hAnsi"), west)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold


def format_body(p):
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(3)
    for run in p.runs:
        set_run_font(run)


def format_heading3(p):
    p.paragraph_format.first_line_indent = None
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    for run in p.runs:
        set_run_font(run, east="黑体", west="Arial", size=10.5, bold=True)


def insert_before(anchor, items):
    for text, style in items:
        p = anchor.insert_paragraph_before(text, style=style)
        if style == "Heading 3":
            format_heading3(p)
        else:
            format_body(p)


doc = Document(str(DOCX))

mission2_anchor = None
mission3_anchor = None
for p in doc.paragraphs:
    text = p.text.strip()
    if text.startswith("2.2  Mission03"):
        mission2_anchor = p
    if text.startswith("3  综合分析"):
        mission3_anchor = p

if mission2_anchor is None or mission3_anchor is None:
    raise RuntimeError("Could not locate insertion anchors in the report.")

mission2_items = [
    ("2.1.4  工程权衡与边界条件讨论", "Heading 3"),
    (
        "对于训练停止条件，程序采用连续回合步数稳定而非 ΔQ 小于阈值作为判据。这一选择属于面向演示系统的启发式工程权衡。严格的 ΔQ 判据能够从价值函数层面刻画数学收敛，但需要持续遍历或比较 Q 表内部状态；在当前 PyQt5 可视化系统中，用户更直接关注的是输出轨迹是否稳定。因此，以连续若干回合路径步数一致作为宏观可观测输出的近似稳态指标，能够在较低计算开销下支持交互式演示。需要强调的是，该规则并不等价于 Q 表全局收敛证明，而是面向课堂实验场景的停止准则。",
        "Normal",
    ),
    (
        "对于 ε 贪心策略，程序保留固定的 e_greedy = 0.9，即维持 10% 的随机探索概率。若环境完全静态，引入 ε 衰减通常可以提高后期收敛效率；然而，固定探索率可以为潜在的动态迷宫扩展保留持续激励特性，使智能体在障碍物拓扑变化或早期策略陷入局部最优时仍有机会发现替代路径。因此，该参数设计更偏向鲁棒性和可扩展性，而非单次静态迷宫的最快收敛。",
        "Normal",
    ),
    (
        "对于随机障碍物生成，当前实现只进行数量阈值检查，尚未通过 BFS 或并查集等方法验证起点与终点的连通性。该设计使不可达迷宫成为算法边界条件的一部分：当环境拓扑不存在可行路径时，智能体无法获得终点正奖励，系统可能表现为无法收敛或仅在可达区域内反复更新 Q 值。该现象反映了环境物理约束对学习结果的限制。若将系统从教学演示推进到稳定应用，则应在生成阶段加入连通性验证，以保证每个训练实例都存在可达目标。",
        "Normal",
    ),
]

mission3_items = [
    ("2.2.4  推理策略与扩展文件说明", "Heading 3"),
    (
        "在冲突消解方面，程序首先按照规则优先级升序排序，再按照前提条件数量降序排序。当两条规则在上述两个维度完全相同时，Python 稳定排序会保留 JSON 知识库中的加载顺序，从而形成确定性的序列回退策略。该设计避免了随机选择规则导致的推理结果不稳定，使同一事实输入在重复运行中得到可复现输出。对于规模更大的专家系统，可进一步显式加入规则编号、置信度或专家权重作为第三层 tie-breaker。",
        "Normal",
    ),
    (
        "在环路控制方面，当前系统未在 KnowledgeBase 初始化阶段执行全量拓扑图环路检测，而是在候选推荐函数 get_all_dependencies 中使用 visited 集合对局部递归路径进行阻断。这是一种惰性计算策略：系统仅在需要展开某个目标动物依赖树时检查当前路径是否回访已有结论。该方法降低了启动阶段开销，并足以保证推荐模块不会因局部环路进入无限递归。若知识库扩展至更高规模或用于长期维护，应在导入阶段增加全局有向图校验，以提前发现规则环路和孤立结论。",
        "Normal",
    ),
    (
        "目录中的 yolov8n.pt、vision_expert.py 与 vision_expert2.py 可视为多模态感知方案的探索性基线。初始设计尝试由视觉模型抽取对象事实，再将这些事实输入产生式系统进行符号推理；最终主线保留以 animal_expert2.py 和 knowledge.json 为核心的专家系统实现，以突出课程要求中的产生式机制、冲突消解和解释日志。视觉相关文件仍具有保留价值，因为它们说明了系统可从纯符号推理扩展到感知-推理融合框架，并为后续建立检测类别到语义特征的映射关系提供接口基础。",
        "Normal",
    ),
]

insert_before(mission2_anchor, mission2_items)
insert_before(mission3_anchor, mission3_items)

doc.save(str(DOCX))
print(DOCX)
