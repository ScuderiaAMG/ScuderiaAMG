%% 实验6 — 硬件验证 (C2=1μF, R≤999.9kΩ 约束)
%  滞后校正无源 RC 网络:
%    Input(OUT)──[R1]──┬── Output(H1)
%                       │
%                      [R2]
%                       │
%                      [C2]=1μF
%                       │
%                      GND
%  Gc(s) = (1+sR2C2)/(1+s(R1+R2)C2), β=(R1+R2)/R2, T=R2C2

clear; clc; close all;

fprintf('╔══════════════════════════════════════════════╗\n');
fprintf('║  实验6 滞后校正 — 硬件验证                 ║\n');
fprintf('║  约束: C2=1μF, R1,R2≤999.9kΩ              ║\n');
fprintf('╚══════════════════════════════════════════════╝\n\n');

% ========================================================================
%% 1. 原系统
% ========================================================================
G_orig = tf(30, [0.3, 1, 0]);
G_cl_orig = feedback(G_orig, 1);
[~, Pm0, ~, Wcp0] = margin(G_orig);
info0 = stepinfo(G_cl_orig);

fprintf('原系统: G(s)=30/[s(0.3s+1)]  PM=%.2f°  ωc=%.3f\n\n', Pm0, Wcp0);

% ========================================================================
%% 2. 约束下最优设计 (R1=R2=999kΩ → PM≈22°)
% ========================================================================
C2 = 1e-6;
R2 = 999e3;
R1 = 999e3;
T_act = R2 * C2;
beta_act = (R1 + R2) / R2;

num_c = [T_act, 1];
den_c = [beta_act * T_act, 1];
Gc = tf(num_c, den_c);
G_comp = G_orig * Gc;
G_cl_comp = feedback(G_comp, 1);

[~, Pm_comp, ~, Wcp_comp] = margin(G_comp);
info_comp = stepinfo(G_cl_comp);

fprintf('====== 约束下最优设计 ======\n');
fprintf('  R1=%.0fkΩ, R2=%.0fkΩ, C2=1μF\n', R1/1e3, R2/1e3);
fprintf('  T=%.4fs, β=%.2f\n', T_act, beta_act);
fprintf('  Gc(s)=(%.4fs+1)/(%.4fs+1)\n', T_act, beta_act*T_act);
fprintf('  高频衰减=%.1fdB\n', -20*log10(beta_act));
fprintf('  ─────────────────────────\n');
fprintf('  校正后 PM=%.2f° (原%.2f°)  Δ=+%.2f°\n', Pm_comp, Pm0, Pm_comp-Pm0);
fprintf('  超调: %.1f%%→%.1f%%  ts:%.3fs→%.3fs\n', ...
        info0.Overshoot, info_comp.Overshoot, ...
        info0.SettlingTime, info_comp.SettlingTime);
fprintf('\n  ⚠ PM=%.1f°<40° — C2=1μF+R≤1MΩ的物理极限\n', Pm_comp);

% 计算需要多大C2才能达到PM=40°
eps40 = 10; k40 = 5;
wc40 = cotd(40 + eps40) / 0.3;
beta40 = 30 / (wc40 * sqrt(0.09*wc40^2 + 1));
T40 = k40 / wc40;
C2_need_40 = T40 / 999.9e3;
fprintf('  达PM=40°需C2≥%.1fμF (或R2≥%.0fkΩ)\n\n', C2_need_40*1e6, T40/C2/1e3);

% ========================================================================
%% 3. D5区电阻测量 (比例环节法)
% ========================================================================
fprintf('====== D5区电阻量程测量 ======\n');
fprintf('  反相比例: Vout = -(Rx/R_ref)×Vin\n');
fprintf('  R_ref=100kΩ, Vin=1.0V → Rx=|Vout|×100kΩ\n\n');

fprintf('  实测记录:\n');
fprintf('  ┌─────┬──────────┬──────────┬────────────┐\n');
fprintf('  │ 序号│ Vout (V) │ Rx (kΩ)  │ 备注       │\n');
fprintf('  ├─────┼──────────┼──────────┼────────────┤\n');
fprintf('  │  1  │  ______  │  ______  │ 最小位置   │\n');
fprintf('  │  2  │  ______  │  ______  │ 中间       │\n');
fprintf('  │  3  │  ______  │  ______  │ 最大位置   │\n');
fprintf('  └─────┴──────────┴──────────┴────────────┘\n');
fprintf('  可用量程: ______ kΩ ~ ______ kΩ\n\n');

% ========================================================================
%% 4. 绘图对比
% ========================================================================
t_sim = 0:0.01:10;

figure('Name', '硬件验证 — C2=1μF约束', 'Color', 'w', ...
       'Position', [50, 50, 1000, 500]);

subplot(1,2,1);
step(G_cl_orig, t_sim, 'b--', 'LineWidth', 1.5);
hold on;
step(G_cl_comp, t_sim, 'r-', 'LineWidth', 2);
grid on;
legend(sprintf('原系统 PM=%.1f° 超调%.1f%%', Pm0, info0.Overshoot), ...
       sprintf('校正后 PM=%.1f° 超调%.1f%%\nR1=R2=999kΩ C2=1μF', ...
               Pm_comp, info_comp.Overshoot), ...
       'Location', 'best');
xlabel('时间 t (s)'); ylabel('输出');
title('阶跃响应 (C2=1μF, R≤1MΩ)');

subplot(1,2,2);
margin(G_orig);
hold on;
margin(G_comp);
grid on;
legend('原系统', '校正后 (C2=1μF, R1=R2=999kΩ)', 'Location', 'southwest');
title('Bode图对比');

saveas(gcf, 'lag_硬件验证_C2_1uF.png');

% ========================================================================
%% 5. 时域指标汇总
% ========================================================================
fprintf('====== 时域指标汇总 ======\n\n');
fprintf('  ┌──────────────┬──────────┬──────────┐\n');
fprintf('  │    指标      │  校正前  │  校正后  │\n');
fprintf('  ├──────────────┼──────────┼──────────┤\n');
fprintf('  │ 超调量 (%%)  │ %7.1f  │ %7.1f  │\n', ...
        info0.Overshoot, info_comp.Overshoot);
fprintf('  │ 调节时间 (s) │ %7.3f  │ %7.3f  │\n', ...
        info0.SettlingTime, info_comp.SettlingTime);
fprintf('  │ 峰值时间 (s) │ %7.3f  │ %7.3f  │\n', ...
        info0.PeakTime, info_comp.PeakTime);
fprintf('  │ 相位裕度 (°) │ %7.2f  │ %7.2f  │\n', Pm0, Pm_comp);
fprintf('  └──────────────┴──────────┴──────────┘\n\n');

fprintf('====== 接线步骤 ======\n');
fprintf('  1. 测量D5区可调电阻量程 (比例环节, R_ref=100kΩ)\n');
fprintf('  2. R2调至最大 (~999kΩ), 并联在H1与GND之间\n');
fprintf('  3. R1调至最大 (~999kΩ), 串联在OUT与H1之间\n');
fprintf('  4. C2=1μF并联在R2两端\n');
fprintf('  5. 测量校正后系统的阶跃响应和Bode图\n');
fprintf('  6. 对比仿真: PM期望≈22°, 确认测量值\n');
fprintf('  7. 实验报告中讨论为何PM<40°及改进方案\n');
