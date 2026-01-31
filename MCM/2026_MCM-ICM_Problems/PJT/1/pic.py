import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import colorsys

# --- Configuration ---
# Set general style params
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

def generate_pastel_colors(n_colors=6, saturation=0.5, brightness=0.85):
    """
    Generate a palette of distinct pastel colors with fixed saturation and brightness.
    """
    colors = []
    for i in range(n_colors):
        hue = i / n_colors
        # Convert HSV to RGB
        rgb = colorsys.hsv_to_rgb(hue, saturation, brightness)
        colors.append(rgb)
    return colors

def main():
    # 1. Load Data
    try:
        df = pd.read_csv('predicted_vote_shares_sorted.csv')
    except FileNotFoundError:
        print("Error: 'predicted_vote_shares_sorted.csv' not found.")
        return

    # 2. Preprocess Data
    # Clean Industry: Fix capitalization and group small categories
    df['industry'] = df['industry'].str.title().str.strip()
    top_industries = df['industry'].value_counts().nlargest(5).index
    df['Industry_Group'] = df['industry'].apply(lambda x: x if x in top_industries else 'Other')

    # Convert is_eliminated to explicit String Categories for safety
    # This fixes the "missing keys" ValueError
    df['Status'] = df['is_eliminated'].apply(lambda x: 'Eliminated' if int(x) == 1 else 'Safe')

    # Define Color Palette (Light, Pastel, S=0.5, V=0.85)
    custom_palette = generate_pastel_colors(n_colors=6, saturation=0.5, brightness=0.85)
    # Assign specific colors to Status
    status_palette = {'Safe': custom_palette[2], 'Eliminated': custom_palette[0]} # Greenish and Reddish
    
    # 3. Create Dashboard
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), facecolor='white')
    fig.suptitle('Competition Overview: Scores, Votes, and Demographics', fontsize=20, color='#333333', y=0.95)

    # --- Plot 1: Correlation (Judge Scores vs. Vote Share) ---
    ax1 = axes[0, 0]
    sns.scatterplot(
        data=df, 
        x='judge_score_total', 
        y='vote_share_hat', 
        hue='Status', 
        palette=status_palette,
        alpha=0.6, 
        edgecolor=None,
        ax=ax1
    )
    ax1.set_title('Judge Score vs. Predicted Vote Share', fontsize=14, color='#555555')
    ax1.set_xlabel('Total Judge Score', fontsize=11, color='#555555')
    ax1.set_ylabel('Predicted Vote Share', fontsize=11, color='#555555')
    # Update legend to remove internal title if desired, or keep it
    ax1.legend(title='Status', frameon=False)
    ax1.grid(True, linestyle='--', alpha=0.3)

    # --- Plot 2: Industry Performance (Bar Chart) ---
    ax2 = axes[0, 1]
    industry_order = df.groupby('Industry_Group')['vote_share_hat'].mean().sort_values(ascending=False).index
    
    # Fix: Assign hue=x variable to satisfy new seaborn requirements
    sns.barplot(
        data=df, 
        x='Industry_Group', 
        y='vote_share_hat', 
        hue='Industry_Group', 
        order=industry_order,
        palette=custom_palette[:len(industry_order)],
        ax=ax2,
        errorbar=None,
        legend=False # Hide legend as it duplicates x-axis
    )
    ax2.set_title('Average Vote Share by Industry', fontsize=14, color='#555555')
    ax2.set_xlabel('Industry', fontsize=11, color='#555555')
    ax2.set_ylabel('Avg Predicted Vote Share', fontsize=11, color='#555555')
    ax2.tick_params(axis='x', rotation=15)
    ax2.grid(axis='y', linestyle='--', alpha=0.3)

    # --- Plot 3: Weekly Progression (Line Plot) ---
    ax3 = axes[1, 0]
    sns.lineplot(
        data=df, 
        x='week', 
        y='vote_share_hat', 
        hue='Status', 
        palette=status_palette,
        style='Status',
        markers=True,
        dashes=False,
        ax=ax3,
        errorbar=('ci', 95)
    )
    ax3.set_title('Vote Share Trends Over Weeks', fontsize=14, color='#555555')
    ax3.set_xlabel('Week Number', fontsize=11, color='#555555')
    ax3.set_ylabel('Mean Vote Share', fontsize=11, color='#555555')
    ax3.legend(title='Status', loc='upper left', frameon=False)
    ax3.grid(True, linestyle='--', alpha=0.3)

    # --- Plot 4: Elimination Distribution (Box Plot) ---
    ax4 = axes[1, 1]
    # Fix: Assign hue=x variable to satisfy new seaborn requirements
    sns.boxplot(
        data=df, 
        x='Status', 
        y='vote_share_hat', 
        hue='Status',
        palette=status_palette,
        width=0.5,
        fliersize=3,
        linewidth=1.5,
        ax=ax4,
        legend=False # Hide legend as it duplicates x-axis
    )
    ax4.set_title('Vote Share Distribution: Safe vs. Eliminated', fontsize=14, color='#555555')
    ax4.set_xlabel('Status', fontsize=11, color='#555555')
    ax4.set_ylabel('Predicted Vote Share', fontsize=11, color='#555555')
    ax4.grid(axis='y', linestyle='--', alpha=0.3)

    # Final Layout Adjustments
    sns.despine(trim=True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    # Save
    plt.savefig('Competition_Overview_Dashboard.png', dpi=300, bbox_inches='tight')
    print("Dashboard saved as 'Competition_Overview_Dashboard.png'")

if __name__ == "__main__":
    main()