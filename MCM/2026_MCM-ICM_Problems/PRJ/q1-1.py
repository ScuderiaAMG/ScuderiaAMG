import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

# ===================== 1. Data Loading & Preprocessing =====================
def load_data(file_path):
    """Read results file and calculate weekly consistency metrics."""
    df = pd.read_excel(file_path, engine='openpyxl')
    weekly_consistency = []

    # Group by 'Season-Week'
    for (season, week), group in df.groupby(['Season', 'Week']):
        # Separate Eliminated / Not Eliminated
        elim_group = group[group['Is_Eliminated'] == 1]['Estimated_Vote_Share']
        not_elim_group = group[group['Is_Eliminated'] == 0]['Estimated_Vote_Share']
        k = len(elim_group)  # Number of people eliminated (1-2)

        if k == 0 or len(not_elim_group) < 2:
            continue  # Skip invalid weeks

        # 1. Vote Share Difference
        vote_diff = not_elim_group.mean() - elim_group.mean()

        # 2. Spearman Correlation
        group['vote_rank'] = group['Estimated_Vote_Share'].rank(ascending=False)
        spearman_corr = group[['vote_rank', 'Is_Eliminated']].corr(method='spearman').iloc[0, 1]

        # 3. Consistency Accuracy
        bottom_k = group.nsmallest(k, 'Estimated_Vote_Share')
        accuracy = bottom_k['Is_Eliminated'].sum() / k

        # 4. CI Coverage
        elim_ci_upper = elim_group.mean() + 1.96 * elim_group.sem()
        not_elim_ci_lower = not_elim_group.mean() - 1.96 * not_elim_group.sem()
        ci_coverage = 1 if elim_ci_upper < not_elim_ci_lower else 0

        weekly_consistency.append({
            'Season_Week': f"S{season}-W{week}",
            'Elim_Mean': elim_group.mean(),
            'Elim_Sem': elim_group.sem(),
            'Not_Elim_Mean': not_elim_group.mean(),
            'Not_Elim_Sem': not_elim_group.sem(),
            'Vote_Diff': vote_diff,
            'Spearman_Corr': spearman_corr,
            'Consistency_Accuracy': accuracy,
            'CI_Coverage': ci_coverage
        })

    return pd.DataFrame(weekly_consistency)


# ===================== 2. Plotting (Modified Style) =====================
def plot_elimination_consistency(data, save_path):
    # --- Style Settings (Light Theme) ---
    plt.rcParams['figure.figsize'] = (16, 10)
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
    plt.style.use('default') # White background

    # Custom Light Colors (HSL approx: S=50%, L=80%)
    COLOR_SAFE = '#8FD8A0'      # Light Green
    COLOR_ELIM = '#F2A6A6'      # Light Red
    COLOR_ACC_HIGH = '#7BC8A4'  # Light Teal (Accuracy >= 0.9)
    COLOR_ACC_MED = '#F2D06B'   # Light Mustard (0.8 <= Accuracy < 0.9)
    COLOR_ACC_LOW = '#E69F9F'   # Light Salmon (Accuracy < 0.8)
    COLOR_TEXT = '#555555'      # Dark Grey for text (softer than black)

    # Create Canvas
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    
    # Ensure white background
    fig.patch.set_facecolor('white')
    ax1.set_facecolor('white')

    # Data Prep
    x = range(len(data))
    x_labels = data['Season_Week'].tolist()
    if len(x) > 30:
        x = x[:30]
        x_labels = x_labels[:30]
        data = data.iloc[:30].copy()

    # --- Left Axis: Vote Shares ---
    ax1.errorbar(
        x, data['Not_Elim_Mean'], yerr=data['Not_Elim_Sem'],
        fmt='o-', color=COLOR_SAFE, linewidth=2.5, markersize=6,
        capsize=4, capthick=2, label='Avg Vote Share (Safe)'
    )

    ax1.errorbar(
        x, data['Elim_Mean'], yerr=data['Elim_Sem'],
        fmt='s--', color=COLOR_ELIM, linewidth=2.5, markersize=6,
        capsize=4, capthick=2, label='Avg Vote Share (Eliminated)'
    )

    # --- Right Axis: Consistency Accuracy ---
    colors = []
    for acc in data['Consistency_Accuracy']:
        if acc < 0.8:
            colors.append(COLOR_ACC_LOW)
        elif acc < 0.9:
            colors.append(COLOR_ACC_MED)
        else:
            colors.append(COLOR_ACC_HIGH)

    # Base line
    ax2.plot(
        x, data['Consistency_Accuracy'],
        marker='^', linewidth=2, markersize=7,
        color='#CCCCCC', alpha=0.5  # Very light grey base
    )
    
    # Colored segments and points
    for i in range(len(x) - 1):
        ax2.plot(
            [x[i], x[i + 1]], [data.iloc[i]['Consistency_Accuracy'], data.iloc[i + 1]['Consistency_Accuracy']],
            color=colors[i], linewidth=3
        )
        ax2.scatter(
            x[i], data.iloc[i]['Consistency_Accuracy'],
            color=colors[i], s=80, edgecolor='white', linewidth=1.5, zorder=5
        )
    ax2.scatter(x[-1], data.iloc[-1]['Consistency_Accuracy'], color=colors[-1], s=80, edgecolor='white', linewidth=1.5, zorder=5)

    # --- Annotations for Anomalies ---
    abnormal = data[data['Consistency_Accuracy'] < 0.8]
    for idx, row in abnormal.iterrows():
        pos = x[data.index == idx][0]
        ax2.annotate(
            f"{row['Season_Week']}\nAcc:{row['Consistency_Accuracy']:.2f}",
            xy=(pos, row['Consistency_Accuracy']),
            xytext=(pos, row['Consistency_Accuracy'] - 0.1),
            ha='center', fontsize=9, fontweight='bold', color=COLOR_TEXT,
            arrowprops=dict(arrowstyle='->', color=COLOR_ACC_LOW, lw=1.5),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor=COLOR_ACC_LOW)
        )

    # --- Axis Formatting ---
    # Left Axis
    ax1.set_xlabel('Season-Week', fontsize=14, fontweight='bold', color=COLOR_TEXT)
    ax1.set_ylabel('Average Vote Share', fontsize=14, fontweight='bold', color=COLOR_SAFE)
    ax1.tick_params(axis='y', labelcolor=COLOR_SAFE, labelsize=12)
    ax1.set_ylim(0, 0.3)
    ax1.grid(axis='y', alpha=0.3, linestyle='--', linewidth=1, color='#DDDDDD')
    ax1.tick_params(axis='x', colors=COLOR_TEXT)
    ax1.tick_params(axis='y', colors=COLOR_TEXT)

    # Right Axis
    ax2.set_ylabel('Consistency Accuracy', fontsize=14, fontweight='bold', color=COLOR_ACC_LOW)
    ax2.tick_params(axis='y', labelcolor=COLOR_ACC_LOW, labelsize=12)
    ax2.set_ylim(0.6, 1.05)
    ax2.axhline(y=0.8, color=COLOR_ACC_LOW, linestyle='--', alpha=0.7, linewidth=1.5)

    # X-axis Labels
    ax1.set_xticks(x)
    ax1.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=10, color=COLOR_TEXT)

    # --- Legend ---
    legend_elements = [
        Patch(facecolor=COLOR_SAFE, label='Avg Vote Share (Safe)'),
        Patch(facecolor=COLOR_ELIM, label='Avg Vote Share (Eliminated)'),
        Patch(facecolor=COLOR_ACC_HIGH, label='High Accuracy (>=0.9)'),
        Patch(facecolor=COLOR_ACC_MED, label='Medium Accuracy (0.8-0.9)'),
        Patch(facecolor=COLOR_ACC_LOW, label='Low Accuracy (<0.8)'),
        Patch(facecolor='none', edgecolor=COLOR_ACC_LOW, linestyle='--', label='Excellent Threshold (0.8)')
    ]
    ax1.legend(handles=legend_elements, loc='upper left', fontsize=11, framealpha=0.9, edgecolor='#EEEEEE')

    # Title
    plt.title('Figure 1: Consistency Analysis of Vote Estimation vs Elimination\n(with 95% Confidence Interval)',
              fontsize=16, fontweight='bold', pad=20, color=COLOR_TEXT)

    # Save
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"\n✅ Plot saved to: {save_path}")
    print(f"📊 Statistics (First 30 Weeks):")
    print(f"  - Avg Vote Diff: {data['Vote_Diff'].mean():.4f}")
    print(f"  - Avg Spearman Corr: {data['Spearman_Corr'].mean():.4f}")
    print(f"  - Avg Accuracy: {data['Consistency_Accuracy'].mean():.4f}")
    print(f"  - CI Coverage: {data['CI_Coverage'].mean():.4f}")


if __name__ == '__main__':
    # REPLACE with your path
    file_path = r"D:\EP_FROM_Model_Final_Results.xlsx"
    save_path = r"D:\Elimination_Consistency_Analysis_English.png"

    # Only run if file exists (mock run for safety in some envs, usually just run)
    try:
        consistency_data = load_data(file_path)
        plot_elimination_consistency(consistency_data, save_path)
    except Exception as e:
        print(f"Execution skipped or failed: {e}")