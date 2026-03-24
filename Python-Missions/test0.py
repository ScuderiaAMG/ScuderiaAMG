import graphviz

def draw_control_system():
    # 创建一个有向图对象，格式设为 png (也可以设为 pdf 或 svg)
    dot = graphviz.Digraph(comment='Block Diagram', format='png')
    
    # 全局属性设置：从左到右绘制 (LR)，并统一字体和排版
    dot.attr(rankdir='LR', nodesep='0.8', ranksep='1.0')
    dot.attr('node', fontname='Arial', fontsize='12')
    dot.attr('edge', fontname='Arial', fontsize='10')

    # 1. 定义节点 (Nodes)
    # 输入与输出信号 (纯文本格式)
    dot.node('R', 'R(s)', shape='plaintext')
    dot.node('C', 'C(s)', shape='plaintext')

    # 相加点/比较点 (圆形)
    # 使用 width 固定大小，使其看起来像标准的相加点
    dot.node('Sum1', 'Σ', shape='circle', fixedsize='true', width='0.4')
    dot.node('Sum2', 'Σ', shape='circle', fixedsize='true', width='0.4')
    dot.node('Sum3', 'Σ', shape='circle', fixedsize='true', width='0.4')

    # 传递函数模块 (矩形)
    dot.node('G1', 'G1', shape='box', width='0.6', height='0.4')
    dot.node('G2', 'G2', shape='box', width='0.6', height='0.4')
    dot.node('G3', 'G3', shape='box', width='0.6', height='0.4')
    dot.node('G4', 'G4', shape='box', width='0.6', height='0.4')
    dot.node('H1', 'H1', shape='box', width='0.6', height='0.4')
    dot.node('H2', 'H2', shape='box', width='0.6', height='0.4')
    dot.node('G5', 'G5', shape='box', width='0.6', height='0.4') # 假设的并联或前馈模块

    # 2. 定义连接线 (Edges) 与信号极性
    # 主干前向通路
    dot.edge('R', 'Sum1')
    dot.edge('Sum1', 'G1')
    dot.edge('G1', 'Sum2')
    dot.edge('Sum2', 'G2')
    dot.edge('G2', 'Sum3')
    dot.edge('Sum3', 'G3')
    dot.edge('G3', 'G4')
    dot.edge('G4', 'C')

    # 局部反馈与前馈回路
    # 注意：这里的连接逻辑是根据你原图第一步的大致结构推断的
    # xlabel 用于在箭头附近标注 '+' 或 '-'
    
    # H2 反馈回路
    dot.edge('G1', 'H2', headport='e', tailport='e') # 从 G1 后引出
    dot.edge('H2', 'Sum1', xlabel='-', headport='s') # 负反馈接入 Sum1

    # H1 反馈回路
    dot.edge('G3', 'H1', headport='e', tailport='e') # 从 G3 后引出
    dot.edge('H1', 'Sum2', xlabel='-', headport='s') # 负反馈接入 Sum2
    
    # 顶部前馈回路 (对应你图中标注“后移”的红色箭头区域)
    dot.edge('R', 'G5')
    dot.edge('G5', 'Sum2', xlabel='+') 

    # 3. 渲染并保存图片
    # view=True 会在生成后自动打开图片
    dot.render('block_diagram_step_1', view=True)
    print("图表已生成：block_diagram_step_1.png")

if __name__ == '__main__':
    draw_control_system()