import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_visualizations():
    # ==========================================
    # 1. 数据加载与预处理
    # ==========================================
    input_file = "Optimized_Algorithm_Results.csv"
    try:
        df = pd.read_csv(input_file)
        print(f"Successfully loaded {input_file}")
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found. Please ensure it is in the same directory.")
        return

    # --- 核心逻辑：标记淘汰类型 ---
    # 我们需要区分“正常因分低淘汰”和“因评委否决权(Veto)淘汰”
    df['Status'] = 'Safe'
    
    # 按赛季和周分组处理
    for (season, week), group in df.groupby(['season', 'week']):
        # 如果本周没人被淘汰（如决赛周），跳过
        if group['Is_Eliminated'].sum() == 0:
            continue
            
        # 找到被淘汰者的索引
        elim_indices = group[group['Is_Eliminated'] == 1].index
        # 找到本周最低的综合分
        min_score = group['Composite_Score'].min()
        
        for idx in elim_indices:
            # 判定逻辑：如果被淘汰者的综合分 显著高于 最低分 (考虑浮点误差)
            # 说明他不是倒数第一，但因为裁判分低被强制淘汰 -> Judge Veto
            if df.loc[idx, 'Composite_Score'] > min_score + 0.00001:
                df.loc[idx, 'Status'] = 'Eliminated (Judge Veto)'
            else:
                df.loc[idx, 'Status'] = 'Eliminated (Low Score)'

    # ==========================================
    # 2. 全局绘图风格设置 (学术/浅色系)
    # ==========================================
    plt.rcParams.update({
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans'],
        'text.color': '#555555',
        'axes.labelcolor': '#555555',
        'xtick.color': '#555555',
        'ytick.color': '#555555',
        'axes.edgecolor': '#E0E0E0',
        'axes.grid': True,
        'grid.color': '#F5F5F5',
        'grid.linestyle': '--',
        'figure.dpi': 300
    })

    # 定义配色方案 (低饱和度/浅色)
    # 蓝色=安全，红色=低分淘汰，橙色=评委否决
    colors = {
        'Safe': '#A0C4FF',                   # Pastel Blue
        'Eliminated (Low Score)': '#FFADAD', # Pastel Red
        'Eliminated (Judge Veto)': '#FFD6A5' # Pastel Orange
    }

    # ==========================================
    # 3. 生成图表
    # ==========================================

    # --- 图表 1: The Fairness Field (散点图) ---
    print("Generating Figure 1: Scatter Plot...")
    fig1, ax1 = plt.subplots(figsize=(10, 8))
    
    sns.scatterplot(
        data=df, 
        x='Z_Fan', 
        y='Z_Judge', 
        hue='Status', 
        palette=colors, 
        style='Status',
        markers={'Safe': 'o', 'Eliminated (Low Score)': 'X', 'Eliminated (Judge Veto)': 'X'},
        s=100, 
        alpha=0.75, 
        edgecolor='white', 
        linewidth=0.5, 
        ax=ax1
    )
    
    ax1.set_title('The Fairness Field: Judge vs. Fan Impact (Z-Scores)', fontsize=16, pad=15, fontweight='bold')
    ax1.set_xlabel('Fan Popularity (Standardized Z-Score)', fontsize=12)
    ax1.set_ylabel('Technical Merit (Judge Z-Score)', fontsize=12)
    
    # 添加中心参考线
    ax1.axhline(0, color='#CCCCCC', linestyle='--', linewidth=1)
    ax1.axvline(0, color='#CCCCCC', linestyle='--', linewidth=1)
    
    # 优化图例
    ax1.legend(title='Outcome', title_fontsize='11', fontsize='10', loc='upper left', bbox_to_anchor=(1, 1), frameon=False)
    
    plt.tight_layout()
    fig1.savefig('Figure1_Fairness_Field.png', bbox_inches='tight')
    plt.close(fig1)

    # --- 图表 2: Technical Merit Protection (箱线图) ---
    print("Generating Figure 2: Box Plot...")
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    
    order = ['Safe', 'Eliminated (Judge Veto)', 'Eliminated (Low Score)']
    
    sns.boxplot(
        data=df, 
        x='Status', 
        y='judge_score_total', 
        order=order, 
        palette=colors,
        width=0.6, 
        linewidth=1.5, 
        fliersize=3, 
        boxprops=dict(alpha=0.9),
        ax=ax2
    )
    
    ax2.set_title('Proof of Meritocracy: Judge Scores by Outcome', fontsize=16, pad=15, fontweight='bold')
    ax2.set_ylabel('Raw Total Judge Score', fontsize=12)
    ax2.set_xlabel('')
    ax2.tick_params(axis='x', rotation=0) # 保持标签水平
    
    plt.tight_layout()
    fig2.savefig('Figure2_Merit_Protection.png', bbox_inches='tight')
    plt.close(fig2)

    # --- 图表 3: The "Bobby Bones" Correction (时间线图) ---
    print("Generating Figure 3: Timeline...")
    target_star = "Bobby Bones"
    target_season = 27
    
    subset = df[(df['season'] == target_season) & (df['celebrity_name'] == target_star)].sort_values('week')
    
    if not subset.empty:
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        
        # 绘制三条线
        ax3.plot(subset['week'], subset['Z_Judge'], label='Judge Z-Score', color='#FFADAD', linewidth=2, linestyle='--')
        ax3.plot(subset['week'], subset['Z_Fan'], label='Fan Vote Z-Score', color='#A0C4FF', linewidth=2, linestyle='--')
        ax3.plot(subset['week'], subset['Composite_Score'], label='Composite Score', color='#B5EAD7', linewidth=3)
        
        # 标记淘汰点
        elim_week_rows = subset[subset['Is_Eliminated'] == 1]
        if not elim_week_rows.empty:
            elim_week = elim_week_rows['week'].min()
            
            # 垂直红线
            ax3.axvline(elim_week, color='#FFD6A5', linestyle='-', linewidth=2, alpha=0.8)
            
            # 淘汰文本标记
            ax3.text(elim_week + 0.1, ax3.get_ylim()[1]*0.8, 
                     f'Eliminated by New System\n(Week {int(elim_week)})', 
                     color='#E69A8D', fontweight='bold', fontsize=10)
            
            # 淘汰点标记 X
            ax3.scatter(elim_week, subset.loc[subset['week'] == elim_week, 'Composite_Score'], 
                        color='#FFD6A5', s=200, marker='X', zorder=5, label='Elimination Event')

        ax3.set_title(f"System Stress Test: The '{target_star}' Correction (Season {target_season})", fontsize=16, pad=15, fontweight='bold')
        ax3.set_xlabel('Competition Week', fontsize=12)
        ax3.set_ylabel('Standardized Score (Z-Score)', fontsize=12)
        ax3.axhline(0, color='#CCCCCC', linestyle='-')
        ax3.legend(loc='lower right', frameon=True, framealpha=0.9)
        
        plt.tight_layout()
        fig3.savefig('Figure3_Bobby_Bones_Timeline.png', bbox_inches='tight')
        plt.close(fig3)
    else:
        print(f"Warning: {target_star} not found in data. Skipping Figure 3.")

    # --- 图表 4: Variance Balancing (密度分布图) ---
    print("Generating Figure 4: Density Plot...")
    fig4, (ax4a, ax4b) = plt.subplots(1, 2, figsize=(16, 6))

    # 子图 A: 原始分数的失衡 (BEFORE)
    sns.kdeplot(df['judge_score_total'], ax=ax4a, color='#FFADAD', label='Raw Judge Scores', linewidth=2, fill=True, alpha=0.3)
    ax4a_twin = ax4a.twinx() # 双Y轴，因为量级完全不同
    sns.kdeplot(df['vote_share_hat'], ax=ax4a_twin, color='#A0C4FF', label='Raw Fan Vote Share', linewidth=2, fill=True, alpha=0.3)
    
    ax4a.set_title('BEFORE: The Imbalance (Raw Scores)', fontsize=14, fontweight='bold')
    ax4a.set_xlabel('Score Value')
    ax4a.set_ylabel('Judge Score Density', color='#FFADAD')
    ax4a_twin.set_ylabel('Fan Vote Density', color='#A0C4FF')
    ax4a_twin.set_yticks([]) # 隐藏右侧刻度以保持整洁
    
    # 手动合并图例
    lines, labels = ax4a.get_legend_handles_labels()
    lines2, labels2 = ax4a_twin.get_legend_handles_labels()
    ax4a.legend(lines + lines2, labels + labels2, loc='upper left')

    # 子图 B: 标准化后的平衡 (AFTER)
    sns.kdeplot(df['Z_Judge'], ax=ax4b, color='#FFADAD', label='Standardized Judge Score', linewidth=2, fill=True, alpha=0.3)
    sns.kdeplot(df['Z_Fan'], ax=ax4b, color='#A0C4FF', label='Standardized Fan Vote', linewidth=2, linestyle='--', fill=True, alpha=0.3)
    
    ax4b.set_title('AFTER: Mathematical Equality (Z-Scores)', fontsize=14, fontweight='bold')
    ax4b.set_xlabel('Standard Deviations (Z-Score)')
    ax4b.set_ylabel('Density')
    ax4b.set_xlim(-4, 4)
    ax4b.legend(loc='upper right')

    plt.tight_layout()
    fig4.savefig('Figure4_Variance_Balance.png', bbox_inches='tight')
    plt.close(fig4)

    print("All visualizations generated and saved successfully.")

if __name__ == "__main__":
    generate_visualizations()