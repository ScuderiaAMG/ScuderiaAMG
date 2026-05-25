%% ============================================================
% 实验5核心：频率特性法的计算机研究
% 使用 MATLAB R2026a 的交互式工具
% ============================================================
% 使用方法：
%   1. 运行本脚本查看基本分析
%   2. 在命令窗口输入 controlSystemDesigner 打开交互式设计器
%   3. 在命令窗口输入 rltool 打开根轨迹设计器
% ============================================================
clear; close all; clc;

fprintf('========================================\n');
fprintf('  实验5：频率特性法计算机研究\n');
fprintf('  MATLAB R2026a\n');
fprintf('========================================\n\n');

%% ----- 传递函数定义（作业题10个）-----
% G1 = 2/[(s+1)(s^2+s+1)]
% G2 = 1/[(0.8s+1)(s^2+s+1)]
% G3 = 2/[(s+1)(s^2+0.8s+1)]
% G4 = 2/[(s+1)(s^2+1.2s+1)]
% G5 = 2/[(1.2s+1)(s^2+s+1)]
% G6 = 2/[(2s+1)(s^2+s+1)]
% G7 = 2/[(s+1)(s^2+2s+1)]
% G8 = 2/[(0.6s+1)(s^2+1.2s+1)]
% G9 = 2/[(5s+1)(s^2+s+1)]
% G10= 2/[(4s+1)(s^2+0.75s+1)]

sys_names = {
    'G_1: 2/[(s+1)(s^2+s+1)]';
    'G_2: 1/[(0.8s+1)(s^2+s+1)]';
    'G_3: 2/[(s+1)(s^2+0.8s+1)]';
    'G_4: 2/[(s+1)(s^2+1.2s+1)]';
    'G_5: 2/[(1.2s+1)(s^2+s+1)]';
    'G_6: 2/[(2s+1)(s^2+s+1)]';
    'G_7: 2/[(s+1)(s^2+2s+1)]';
    'G_8: 2/[(0.6s+1)(s^2+1.2s+1)]';
    'G_9: 2/[(5s+1)(s^2+s+1)]';
    'G_10: 2/[(4s+1)(s^2+0.75s+1)]';
};

G = {
    tf(2, conv([1,1], [1,1,1]));
    tf(1, conv([0.8,1], [1,1,1]));
    tf(2, conv([1,1], [1,0.8,1]));
    tf(2, conv([1,1], [1,1.2,1]));
    tf(2, conv([1.2,1], [1,1,1]));
    tf(2, conv([2,1], [1,1,1]));
    tf(2, conv([1,1], [1,2,1]));
    tf(2, conv([0.6,1], [1,1.2,1]));
    tf(2, conv([5,1], [1,1,1]));
    tf(2, conv([4,1], [1,0.75,1]));
};

%% ----- 1. Nyquist 图（奈奎斯特曲线）-----
fprintf('绘制 Nyquist 图...\n');

figure('Name', '实验5：Nyquist图汇总', 'NumberTitle', 'off', ...
       'Position', [50, 50, 1400, 900]);
tiledlayout(3, 4, 'TileSpacing', 'compact', 'Padding', 'compact');

for i = 1:10
    nexttile;
    nyquist(G{i});
    grid on; axis equal;
    title(sprintf('G_%d', i), 'FontSize', 9);
end
sgtitle('Nyquist图汇总', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, '实验5_Nyquist汇总.png');

%% ----- 2. Bode图详细分析 -----
fprintf('绘制 Bode 图（含裕度标注）...\n');

figure('Name', '实验5：Bode图详细分析', 'NumberTitle', 'off', ...
       'Position', [50, 50, 1400, 900]);
tiledlayout(3, 4, 'TileSpacing', 'compact', 'Padding', 'compact');

stability_info = cell(10, 1);

for i = 1:10
    nexttile;
    [Gm, Pm, Wcg, Wcp] = margin(G{i});
    margin(G{i});
    grid on;

    % 判断闭环稳定性（基于相位裕度）
    if isinf(Gm)
        stab_str = '稳定(Gm=inf)';
    elseif Gm > 1 && Pm > 0
        stab_str = '稳定';
    elseif Gm < 1 || Pm < 0
        stab_str = '不稳定';
    else
        stab_str = '临界稳定';
    end
    stability_info{i} = stab_str;

    title(sprintf('G_%d | Gm=%.1fdB Pm=%.1f° | %s', ...
          i, 20*log10(Gm), Pm, stab_str), 'FontSize', 8);
end
sgtitle('Bode图详细分析（含稳定裕度）', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, '实验5_Bode详细分析.png');

%% ----- 3. 根轨迹图详细分析 -----
fprintf('绘制 根轨迹图...\n');

figure('Name', '实验5：根轨迹详细分析', 'NumberTitle', 'off', ...
       'Position', [50, 50, 1400, 900]);
tiledlayout(3, 4, 'TileSpacing', 'compact', 'Padding', 'compact');

for i = 1:10
    nexttile;
    rlocus(G{i});
    grid on; axis equal;
    [p, z] = pzmap(G{i});
    title(sprintf('G_%d | 极点:%d 零点:%d | %s', ...
          i, length(p), length(z), stability_info{i}), 'FontSize', 8);
end
sgtitle('根轨迹图汇总', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, '实验5_根轨迹详细分析.png');

%% ----- 4. 开环 vs 闭环 频率特性对比 -----
fprintf('对比开环/闭环频率特性...\n');

% 选 G1 作为示例
G_sample = G{1};
T_sample = feedback(G_sample, 1);  % 闭环

figure('Name', '实验5：开环vs闭环频率特性', 'NumberTitle', 'off', ...
       'Position', [100, 100, 1000, 600]);

% 幅频特性对比
subplot(2, 1, 1);
[mag_open, ~, w_open] = bode(G_sample);
[mag_cl, ~, w_cl] = bode(T_sample);
semilogx(w_open, 20*log10(squeeze(mag_open)), 'b-', 'LineWidth', 1.5);
hold on;
semilogx(w_cl, 20*log10(squeeze(mag_cl)), 'r-', 'LineWidth', 1.5);
grid on;
xlabel('频率 (rad/s)'); ylabel('幅值 (dB)');
title('开环 vs 闭环 幅频特性');
legend('开环 G(s)', '闭环 T(s)', 'Location', 'best');

% 相频特性对比
subplot(2, 1, 2);
[~, phase_open, ~] = bode(G_sample);
[~, phase_cl, ~] = bode(T_sample);
semilogx(w_open, squeeze(phase_open), 'b-', 'LineWidth', 1.5);
hold on;
semilogx(w_cl, squeeze(phase_cl), 'r-', 'LineWidth', 1.5);
grid on;
xlabel('频率 (rad/s)'); ylabel('相位 (deg)');
title('开环 vs 闭环 相频特性');
legend('开环 G(s)', '闭环 T(s)', 'Location', 'best');
sgtitle(sprintf('G_1: %s 开环与闭环频率特性对比', sys_names{1}), ...
        'FontSize', 12, 'FontWeight', 'bold');
saveas(gcf, '实验5_开环闭环频率对比.png');

%% ----- 5. 参数变化对系统特性的影响 -----
fprintf('分析参数变化对系统特性的影响...\n');

% 以 G3 = 2/[(s+1)(s^2+0.8s+1)] 为例，改变分子增益
gain_values = [0.5, 1, 2, 4, 8];

figure('Name', '实验5：增益变化影响', 'NumberTitle', 'off', ...
       'Position', [100, 100, 1200, 800]);
tiledlayout(2, 3, 'TileSpacing', 'compact', 'Padding', 'compact');

for j = 1:length(gain_values)
    K = gain_values(j);
    G_var = tf(K, conv([1,1], [1,0.8,1]));
    T_var = feedback(G_var, 1);

    % 根轨迹上的增益点
    nexttile;
    [y, t] = step(T_var, 20);
    plot(t, y, 'LineWidth', 1.5);
    grid on;
    info = stepinfo(T_var);
    title(sprintf('K=%.1f: σ=%.1f%%, t_s=%.2fs', K, info.Overshoot, info.SettlingTime), ...
          'FontSize', 9);
    xlabel('时间 (s)'); ylabel('幅值');
end
sgtitle('不同增益 K 对闭环阶跃响应的影响', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, '实验5_增益变化影响.png');

%% ----- 6. 最小相位与非最小相位系统对比 -----
fprintf('对比最小相位与非最小相位系统...\n');

% 最小相位系统：零极点均在左半平面
G_min = tf([1, 1], [1, 2, 2]);
% 非最小相位系统：右半平面零点
G_nonmin = tf([-1, 1], [1, 2, 2]);

figure('Name', '实验5：最小相位vs非最小相位', 'NumberTitle', 'off', ...
       'Position', [100, 100, 1000, 800]);

% Bode对比
subplot(2, 2, 1);
bode(G_min, 'b-', G_nonmin, 'r--');
grid on;
legend('最小相位', '非最小相位', 'Location', 'best');
title('Bode图对比');

% Nyquist对比
subplot(2, 2, 2);
nyquist(G_min, 'b-');
hold on;
nyquist(G_nonmin, 'r--');
grid on; axis equal;
legend('最小相位', '非最小相位', 'Location', 'best');
title('Nyquist图对比');

% 阶跃响应对比
subplot(2, 2, 3);
T_min = feedback(G_min, 1);
T_nonmin = feedback(G_nonmin, 1);
step(T_min, 'b-', T_nonmin, 'r--', 10);
grid on;
legend('最小相位', '非最小相位', 'Location', 'best');
title('闭环阶跃响应对比');

% 零极点图对比
subplot(2, 2, 4);
pzmap(G_min, 'b');
hold on;
pzmap(G_nonmin, 'r');
grid on;
legend('最小相位', '非最小相位', 'Location', 'best');
title('零极点分布对比');
sgtitle('最小相位系统 vs 非最小相位系统', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, '实验5_最小相位对比.png');

%% ----- 7. 积分环节个数对频率特性的影响 -----
fprintf('分析积分环节个数的影响...\n');

% 0型：无积分环节
G_type0 = tf(10, [1, 1]);
% I型：1个积分环节
G_type1 = tf(10, [1, 1, 0]);
% II型：2个积分环节
G_type2 = tf(10, [1, 1, 0, 0]);

figure('Name', '实验5：积分环节个数影响', 'NumberTitle', 'off', ...
       'Position', [100, 100, 1000, 800]);

subplot(2, 2, 1);
bode(G_type0, 'b-', G_type1, 'r-', G_type2, 'g-');
grid on;
legend('0型', 'I型', 'II型', 'Location', 'best');
title('Bode图对比');

subplot(2, 2, 2);
nyquist(G_type0, 'b-');
hold on;
nyquist(G_type1, 'r-');
nyquist(G_type2, 'g-');
grid on;
legend('0型', 'I型', 'II型', 'Location', 'best');
title('Nyquist图对比（起点与积分个数的关系）');

subplot(2, 2, 3);
T0 = feedback(G_type0, 1);
T1 = feedback(G_type1, 1);
T2 = feedback(G_type2, 1);
step(T0, 'b-', T1, 'r-', T2, 'g-', 10);
grid on;
legend('0型', 'I型', 'II型', 'Location', 'best');
title('闭环阶跃响应对比');

subplot(2, 2, 4);
rlocus(G_type0, 'b-');
hold on;
rlocus(G_type1, 'r-');
rlocus(G_type2, 'g-');
grid on;
legend('0型', 'I型', 'II型', 'Location', 'best');
title('根轨迹对比');
sgtitle('积分环节个数对系统特性的影响', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, '实验5_积分环节影响.png');

%% ----- 汇总报告 -----
fprintf('\n===== 实验5频率特性分析汇总 =====\n\n');

fprintf('【最小相位系统幅相曲线与Bode图特点】\n');
fprintf('  1. 对数幅频与对数相频曲线斜率变化存在确定关系\n');
fprintf('  2. 幅频曲线斜率 -20N dB/dec → 相频趋于 -90N°\n');
fprintf('  3. Bode图中的幅频与相频变化趋势一致\n\n');

fprintf('【幅相曲线起点与积分环节个数的关系】\n');
fprintf('  0型: 起点在正实轴上 (w→0时, |G|=K, ∠G=0°)\n');
fprintf('  I型: 起点在负虚轴无穷远处 (w→0时, |G|→∞, ∠G=-90°)\n');
fprintf('  II型: 起点在负实轴无穷远处 (w→0时, |G|→∞, ∠G=-180°)\n\n');

fprintf('【幅相曲线终点与分子分母阶次的关系】\n');
fprintf('  终点都在原点 |G|→0\n');
fprintf('  终点角度 = -90°×(n-m)，其中 n=分母阶次, m=分子阶次\n\n');

fprintf('【10个系统频率特性汇总】\n');
fprintf('  编号  |  Gm(dB)  |  Pm(deg)  |  闭环稳定性\n');
fprintf('  -------------------------------------------\n');
for i = 1:10
    [Gm, Pm, ~, ~] = margin(G{i});
    fprintf('  G_%2d  |  %7.2f  |  %7.1f   |  %s\n', ...
            i, 20*log10(Gm), Pm, stability_info{i});
end

fprintf('\n程序执行完毕。可输入 controlSystemDesigner 打开交互式设计器。\n');
