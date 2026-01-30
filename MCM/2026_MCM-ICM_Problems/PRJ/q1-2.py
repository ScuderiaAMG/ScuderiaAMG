

# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

# --------------------------
# Paths (Adjust as needed)
# --------------------------
# 请确保这里的路径是正确的，建议直接使用相对路径或绝对路径
# 如果脚本和数据在同一目录下，可以直接写文件名
DATA_PATH = r"D:\2026_MCM_Problem_C_Processed_Data.xlsx" 
OUTPUT_PATH = "4_Season_2_Trajectory_English_Light.png"


def plot_trajectory_final():
    # 1. Read Data
    try:
        # Construct week columns
        week_cols = [f'Weekly_Total_Judge_Score_Week{i}' for i in range(1, 12)]
        
        # --- FIX HERE: Added engine='openpyxl' ---
        df = pd.read_excel(
            DATA_PATH, 
            usecols=['celebrity_name', 'season'] + week_cols, 
            engine='openpyxl'
        )
        print("✅ Data loaded successfully.")
    except Exception as e:
        print(f"❌ Data load failed: {e}")
        return

    # 2. Filter Season 2
    season2_df = df[df['season'] == 2].copy()
    if season2_df.empty:
        print("❌ Season 2 data not found, trying Season 3...")
        season2_df = df[df['season'] == 3].copy()
        if season2_df.empty:
            print("❌ Season 3 data not found, trying Season 1...")
            season2_df = df[df['season'] == 1].copy()

    if season2_df.empty:
        print("❌ No valid season data found.")
        return

    # 3. Clean Week Columns (Keep only valid weeks, e.g., first 6)
    valid_week_cols = []
    for col in week_cols:
        if col in season2_df.columns:
            non_zero_count = season2_df[col].replace(0, np.nan).notna().sum()
            if non_zero_count > 0:
                valid_week_cols.append(col)
    
    # Limit to first 6 weeks for clarity
    valid_week_cols = valid_week_cols[:6]
    
    if len(valid_week_cols) < 2:
        print("❌ Not enough valid weeks to plot.")
        return

    # Extract week numbers
    weeks_num = []
    for col in valid_week_cols:
        week_str = col.split('Week')[-1]
        try:
            weeks_num.append(int(week_str))
        except:
            weeks_num.append(len(weeks_num) + 1)

    # --- 4. Plotting (Modified Light Theme) ---
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
    plt.style.use('default')
    
    plt.figure(figsize=(12, 8))
    
    # Custom Light Palette (10 distinct light colors)
    # HSL-based approximations for S=40-60%, L=70-90%
    LIGHT_PALETTE = [
        '#8CC4E0', # Light Blue
        '#E0B88C', # Light Orange
        '#98E08C', # Light Green
        '#E08C9E', # Light Red
        '#C48CE0', # Light Purple
        '#DFE08C', # Light Yellow/Lime
        '#8CE0D6', # Light Teal
        '#E08CC4', # Light Pink
        '#A6A6A6', # Light Grey
        '#BCAAA4'  # Light Brown
    ]
    
    # Cycle colors if more contestants than colors
    colors = LIGHT_PALETTE * (len(season2_df) // len(LIGHT_PALETTE) + 1)
    
    weeks_label = [f'Week {w}' for w in weeks_num]

    for idx, (_, row) in enumerate(season2_df.iterrows()):
        name = row['celebrity_name']
        if isinstance(name, str) and len(name) > 15:
            name = name[:12] + '...'
            
        scores = []
        for col in valid_week_cols:
            val = row[col]
            # Treat 0 or NaN as missing for plotting continuity
            if pd.notna(val) and val > 0:
                scores.append(val)
            else:
                scores.append(np.nan)
        
        # Plot Line
        plt.plot(weeks_num, scores, 
                 color=colors[idx], 
                 linewidth=2.5, 
                 marker='o', 
                 markersize=6, 
                 label=name,
                 alpha=0.9)

    # Labels and Titles (English)
    COLOR_TEXT = '#555555'
    plt.xlabel('Week', fontsize=12, fontweight='bold', color=COLOR_TEXT)
    plt.ylabel('Weekly Total Judge Score', fontsize=12, fontweight='bold', color=COLOR_TEXT)
    
    plt.title('Figure 4: Contestant Score Trajectory - Season 2\n(Low Judge Scores + Survival = High Fan Support)',
              fontsize=14, fontweight='bold', pad=15, color=COLOR_TEXT)
    
    plt.xticks(weeks_num, weeks_label, fontsize=10, color=COLOR_TEXT)
    plt.yticks(color=COLOR_TEXT)
    
    # Light Grid
    plt.grid(axis='y', alpha=0.4, color='#DDDDDD', linestyle='--')
    
    # Legend
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), 
               fontsize=10, frameon=True, edgecolor='#EEEEEE')

    plt.tight_layout()
    plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ Trajectory plot saved to: {OUTPUT_PATH}")


if __name__ == '__main__':
    print("🚀 Generating Final English Trajectory Plot...")
    plot_trajectory_final()
    print("🎉 Done!")