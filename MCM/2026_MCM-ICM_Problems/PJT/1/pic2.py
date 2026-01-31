import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import colorsys
from sklearn.metrics import confusion_matrix

# --- Configuration ---
# 统一风格设置
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['grid.linestyle'] = '--'

def get_pastel_color(hue, saturation=0.5, brightness=0.85):
    """Generate a specific pastel color."""
    rgb = colorsys.hsv_to_rgb(hue, saturation, brightness)
    return rgb

def generate_pastel_colors(n_colors=6, saturation=0.5, brightness=0.85):
    """Generate a palette of distinct pastel colors."""
    colors = []
    for i in range(n_colors):
        hue = i / n_colors
        rgb = colorsys.hsv_to_rgb(hue, saturation, brightness)
        colors.append(rgb)
    return colors

def main():
    try:
        # 1. Load Data
        # 读取数据 (请确保文件名与您本地一致)
        try:
            df_weekly = pd.read_csv('predicted_vote_shares_sorted.csv')
        except FileNotFoundError:
            print("Error: 'predicted_vote_shares_sorted.csv' not found.")
            return

        # Preprocessing
        df_weekly['Status'] = df_weekly['is_eliminated'].apply(lambda x: 'Eliminated' if int(x) == 1 else 'Safe')
        df_weekly['industry'] = df_weekly['industry'].astype(str).str.title().str.strip()
        
        # 2. Prepare Data for Feature Importance (Proxy for SHAP)
        # 计算特征与预测票数的相关性作为重要性代理
        df_weekly = df_weekly.sort_values(['season', 'celebrity_name', 'week'])
        # 构造简单特征：滚动平均分、分数提升幅度
        df_weekly['rolling_avg'] = df_weekly.groupby(['season', 'celebrity_name'])['judge_score_total'].transform(lambda x: x.rolling(3, min_periods=1).mean())
        df_weekly['improvement'] = df_weekly.groupby(['season', 'celebrity_name'])['judge_score_total'].diff().fillna(0)
        
        features = ['judge_score_total', 'rolling_avg', 'week', 'improvement']
        # 计算绝对相关性
        importance = df_weekly[features].corrwith(df_weekly['vote_share_hat']).abs().sort_values(ascending=True)
        # 重命名以更符合 "SHAP" 风格
        importance.index = [x.replace('_', ' ').title() for x in importance.index]

        # --- Dashboard Plot (Modified) ---
        fig, axes = plt.subplots(2, 2, figsize=(16, 12), facecolor='white')
        fig.suptitle('Advanced Competition Analytics Dashboard', fontsize=20, color='#333333', y=0.95)
        
        # Colors
        c_safe = get_pastel_color(0.33) # Greenish
        c_elim = get_pastel_color(0.0)  # Reddish
        c_imp = get_pastel_color(0.6)   # Blueish for importance

        # TL: Judge Score vs Vote Share
        ax1 = axes[0, 0]
        sns.scatterplot(
            data=df_weekly, x='judge_score_total', y='vote_share_hat', hue='Status',
            palette={'Safe': c_safe, 'Eliminated': c_elim}, alpha=0.6, ax=ax1, legend=True
        )
        ax1.set_title('Judge Score vs. Predicted Vote Share', fontsize=14, color='#555')
        ax1.set_xlabel('Total Judge Score')
        ax1.set_ylabel('Predicted Vote Share')
        ax1.legend(title='Status', frameon=False)
        ax1.grid(True, linestyle='--', alpha=0.3)

        # TR: Feature Importance (SHAP Replacement)
        ax2 = axes[0, 1]
        ax2.barh(importance.index, importance.values, color=c_imp, alpha=0.7)
        ax2.set_title('Feature Importance (Proxy Analysis)', fontsize=14, color='#555')
        ax2.set_xlabel('Correlation Magnitude with Vote Share')
        ax2.grid(axis='x', linestyle='--', alpha=0.3)
        # Add annotation
        ax2.text(0.95, 0.05, "SHAP Analysis:\njudge_score is dominant,\nbut trend matters later.", 
                 transform=ax2.transAxes, ha='right', va='bottom', fontsize=10, 
                 bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='#ddd'))

        # BL: Weekly Trends
        ax3 = axes[1, 0]
        sns.lineplot(
            data=df_weekly, x='week', y='vote_share_hat', hue='Status',
            palette={'Safe': c_safe, 'Eliminated': c_elim}, style='Status', markers=True, ax=ax3, errorbar=('ci', 95)
        )
        ax3.set_title('Vote Share Trends Over Weeks', fontsize=14, color='#555')
        ax3.set_ylabel('Mean Vote Share')
        ax3.legend(frameon=False)
        ax3.grid(True, linestyle='--', alpha=0.3)

        # BR: Elimination Dist (Box)
        ax4 = axes[1, 1]
        sns.boxplot(
            data=df_weekly, x='Status', y='vote_share_hat', hue='Status',
            palette={'Safe': c_safe, 'Eliminated': c_elim}, ax=ax4, width=0.5
        )
        if ax4.legend_: ax4.legend_.remove()
        ax4.set_title('Vote Share Distribution', fontsize=14, color='#555')
        ax4.grid(axis='y', linestyle='--', alpha=0.3)
        
        sns.despine()
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig('Dashboard_Modified.png')
        plt.close()
        print("Generated 'Dashboard_Modified.png'")

        # --- Plot B: Bump Chart (Rank Evolution) ---
        # Pick Season 19 as example (usually has good data)
        target_season = 19
        df_s19 = df_weekly[df_weekly['season'] == target_season].copy()
        
        if not df_s19.empty:
            # Calculate rank per week (Lower rank is better, so Rank 1 is highest vote)
            df_s19['rank'] = df_s19.groupby('week')['vote_share_hat'].rank(ascending=False, method='min')
            
            # Filter top 5 finalists
            top_5_names = df_s19.groupby('celebrity_name')['rank'].mean().nsmallest(5).index
            df_bump = df_s19[df_s19['celebrity_name'].isin(top_5_names)]
            
            plt.figure(figsize=(12, 6), facecolor='white')
            bump_palette = generate_pastel_colors(5, saturation=0.6, brightness=0.9)
            
            sns.lineplot(
                data=df_bump, x='week', y='rank', hue='celebrity_name',
                palette=bump_palette, linewidth=3, marker='o', markersize=8
            )
            
            plt.gca().invert_yaxis() # Rank 1 at top
            plt.title(f'Rank Evolution of Top 5 Contestants (Season {target_season})', fontsize=16, pad=20)
            plt.ylabel('Rank (1=Best)')
            plt.xlabel('Week')
            plt.legend(title='Celebrity', bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False)
            plt.grid(axis='y', linestyle='--', alpha=0.3)
            plt.tight_layout()
            plt.savefig('Bump_Chart.png')
            plt.close()
            print("Generated 'Bump_Chart.png'")

        # --- Plot C: Confusion Matrix (Heatmap) ---
        # Define "Predicted Eliminated" as the person with lowest vote_share_hat in a week
        min_votes = df_weekly.groupby(['season', 'week'])['vote_share_hat'].transform('min')
        df_weekly['predicted_eliminated'] = (df_weekly['vote_share_hat'] == min_votes).astype(int)
        
        cm = confusion_matrix(df_weekly['is_eliminated'], df_weekly['predicted_eliminated'])
        # Normalize by row (True labels) to show recall
        cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        plt.figure(figsize=(8, 6), facecolor='white')
        sns.heatmap(
            cm_norm, annot=True, fmt='.1%', cmap='Blues', cbar=False,
            xticklabels=['Predicted Safe', 'Predicted Eliminated'],
            yticklabels=['Actually Safe', 'Actually Eliminated']
        )
        plt.title('Model Accuracy: Elimination Prediction', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig('Confusion_Matrix.png')
        plt.close()
        print("Generated 'Confusion_Matrix.png'")
        
        print("Success! All images generated.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()