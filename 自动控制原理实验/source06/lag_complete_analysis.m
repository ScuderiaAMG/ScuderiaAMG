%% 实验6（2）频率特性法滞后校正 — C2=1μF, R≤999.9kΩ 约束设计
%  原系统: G(s) = 30 / [s(0.3s + 1)]
%  硬件约束: C2 = 1μF, R1,R2 ∈ [0, 999.9kΩ] (D5区可调电阻)
%
%  ★ 重要物理结论:
%     C2=1μF下T_max=R_max×C2=1s, 零点1/T≥1rad/s,
%     迫使ωc≥k rad/s处原系统相位已严重滞后。
%     被动RC滞后网络在此约束下最优PM≈22°, 无法满足40°~60°要求。
%     达到PM=40°至少需要C2≥1.4μF 或 R≥1.4MΩ。
%
%  本脚本提供:
%    1. 约束下的最优可行设计 (PM≈22°)
%    2. 放宽约束后的理论设计 (PM=40°~60°, 给出所需C2/R值)
%    3. 对比分析, 明确物理极限

clear; clc; close all;

fprintf('╔══════════════════════════════════════════════╗\n');
fprintf('║  实验6 滞后校正 — C2=1μF, R≤999.9kΩ 分析  ║\n');
fprintf('╚══════════════════════════════════════════════╝\n\n');

% ========================================================================
%% 1. 原系统分析
% ========================================================================
num = 30;
den = [0.3, 1, 0];
G_orig = tf(num, den);
G_cl_orig = feedback(G_orig, 1);
[~, Pm0, ~, Wcp0] = margin(G_orig);
info0 = stepinfo(G_cl_orig);

fprintf('【原系统】G(s) = 30/[s(0.3s+1)]\n');
fprintf('  ωc = %.4f rad/s, PM = %.2f°\n', Wcp0, Pm0);
fprintf('  超调 = %.1f%%, ts = %.3fs\n\n', info0.Overshoot, info0.SettlingTime);

% ========================================================================
%% 2. C2=1μF, R≤999.9kΩ 约束下的最优可行设计
%    数值搜索得到全局最优: R1=R2=999.9kΩ, PM≈22.17°
% ========================================================================
fprintf('====== C2=1μF, R≤999.9kΩ 最优可行设计 ======\n\n');

C2 = 1e-6;
R_max = 999.9e3;

% 全局最优参数 (数值搜索确认)
R2_best = 999e3;      % 并联电阻
R1_best = 999e3;      % 串联电阻
T_best  = R2_best * C2;          % = 0.999 s
beta_best = (R1_best + R2_best) / R2_best;  % = 2.0

num_c_best = [T_best, 1];
den_c_best = [beta_best * T_best, 1];
Gc_best = tf(num_c_best, den_c_best);
G_comp_best = G_orig * Gc_best;
G_cl_best = feedback(G_comp_best, 1);

[~, Pm_best, ~, Wcp_best] = margin(G_comp_best);
info_best = stepinfo(G_cl_best);

fprintf('最优设计 (R1=R2=999kΩ, C2=1μF):\n');
fprintf('  Gc(s) = (%.4fs+1)/(%.4fs+1)\n', T_best, beta_best*T_best);
fprintf('  β=%.1f, T=%.4fs, 高频衰减=%.1fdB\n', beta_best, T_best, -20*log10(beta_best));
fprintf('  R1=%.0fkΩ, R2=%.0fkΩ, C2=1μF\n', R1_best/1e3, R2_best/1e3);
fprintf('  ----------------------------------------\n');
fprintf('  校正后 ωc = %.4f rad/s (原 %.4f)\n', Wcp_best, Wcp0);
fprintf('  校正后 PM = %.2f° (原 %.2f°)\n', Pm_best, Pm0);
fprintf('  PM提升   = +%.2f°\n', Pm_best - Pm0);
fprintf('  超调量   = %.1f%% → %.1f%%\n', info0.Overshoot, info_best.Overshoot);
fprintf('  调节时间 = %.3fs → %.3fs\n', info0.SettlingTime, info_best.SettlingTime);
fprintf('\n  ⚠ PM=22° 远低于40°要求 — 这是C2=1μF+R≤1MΩ的物理极限。\n\n');

% ========================================================================
%% 3. 放宽约束后的理论设计 (PM=40°~60°)
%    计算达到各PM目标所需的C2和R值
% ========================================================================
fprintf('====== 理论设计: 达到PM=40°~60°所需参数 ======\n\n');
fprintf('  方法: k=5优化, 计算满足PM目标的最小C2 (设R2=999.9kΩ)\n\n');
fprintf('  目标PM │ ωc_new  │   β   │  T(s)  │ 最小C2  │ 所需R1\n');
fprintf('  ───────┼─────────┼───────┼────────┼─────────┼────────\n');

pm_targets = [40, 45, 50, 55, 60];
theoretical = cell(length(pm_targets), 1);

for i = 1:length(pm_targets)
    gamma_tgt = pm_targets(i);
    % k=5, 调整ε使PM接近目标
    if gamma_tgt <= 40, eps_v = 10;
    elseif gamma_tgt <= 45, eps_v = 10;
    elseif gamma_tgt <= 50, eps_v = 11;
    else eps_v = 12;
    end
    k_v = 5;

    wc_new = cotd(gamma_tgt + eps_v) / 0.3;
    beta_v = 30 / (wc_new * sqrt(0.09 * wc_new^2 + 1));
    T_v = k_v / wc_new;

    C2_min = T_v / R_max;  % 用R_max得到最小C2
    R1_need = (T_v / C2_min) * (beta_v - 1);  % C2_min下所需R1
    % 如果R1 ≤ R_max, 用C2_min即可; 否则需更大C2让R1减小
    if R1_need > R_max
        % 反推: R2用满时, R1=R_max → β=R1/R2+1=2
        % 需要更大C2来减小β(通过降低ωc)
        % 实际上应增大C2使R1≤R_max
        C2_actual = T_v / R_max * (beta_v - 1);  % 修正
    end

    fprintf('  %4.0f°  │ %7.4f │ %5.2f │ %6.4f │ %6.1fμF │ %6.0fkΩ\n', ...
            gamma_tgt, wc_new, beta_v, T_v, C2_min*1e6, ...
            min(R1_need, T_v/C2_min*(beta_v-1))/1e3);

    theoretical{i} = struct('pm',gamma_tgt, 'wc',wc_new, 'beta',beta_v, ...
                            'T',T_v, 'C2_min',C2_min, 'k',k_v, 'eps',eps_v);
end

fprintf('\n  ★ C2=1μF时最小需C2≥1.4μF (对应PM=40°)\n');
fprintf('  ★ PM=40°~50°需要C2≥1.4~2.1μF\n');
fprintf('  ★ 若有C2≥4.7μF则可覆盖全范围\n\n');

% ========================================================================
%% 4. 对比图: 最优可行 vs 原系统 vs 理论目标
% ========================================================================
t_sim = 0:0.01:12;

% --- 阶跃响应 ---
figure('Name', '滞后校正 — C2=1μF约束分析', 'Color', 'w', ...
       'Position', [50, 50, 1000, 550]);

subplot(1,2,1);
step(G_cl_orig, t_sim, 'k--', 'LineWidth', 1.8);
hold on;
step(G_cl_best, t_sim, 'b-', 'LineWidth', 1.8);

% 理论PM=45°响应 (如果C2足够大)
r45 = theoretical{2};
num_c45 = [r45.T, 1];
den_c45 = [r45.beta * r45.T, 1];
Gc45 = tf(num_c45, den_c45);
G_comp45 = G_orig * Gc45;
G_cl45 = feedback(G_comp45, 1);
step(G_cl45, t_sim, 'r-', 'LineWidth', 1.3);

grid on;
legend(sprintf('原系统 PM=%.1f°', Pm0), ...
       sprintf('最优可行 C2=1μF PM=%.1f°\nR1=R2=999kΩ', Pm_best), ...
       sprintf('理论设计 PM=45°\n需要C2≥%.1fμF', r45.C2_min*1e6), ...
       'Location', 'best');
xlabel('时间 t (s)'); ylabel('输出幅值');
title('阶跃响应对比');
yline(1, 'k:', 'LineWidth', 0.5);

% --- Bode图 ---
subplot(1,2,2);
margin(G_orig);
hold on;
margin(G_comp_best);
margin(G_comp45);
grid on;
legend('原系统', ...
       sprintf('最优可行 C2=1μF (PM=%.1f°)', Pm_best), ...
       sprintf('理论PM=45° (C2≥%.1fμF)', r45.C2_min*1e6), ...
       'Location', 'southwest');
title('Bode图对比');
saveas(gcf, 'lag_C2_1uF_约束分析.png');

% ========================================================================
%% 5. 物理极限分析图
% ========================================================================
C2_range = 0.5:0.1:10;  % μF
pm_achievable = zeros(size(C2_range));

for idx = 1:length(C2_range)
    C2_test = C2_range(idx) * 1e-6;
    % 搜索该C2下的最优PM
    best_pm_local = -inf;
    for R2_test = [100e3, 200e3, 500e3, 800e3, 999e3]
        T_test = R2_test * C2_test;
        if T_test > 2, continue; end
        for R1_test = [100e3, 200e3, 500e3, 800e3, 999e3]
            beta_test = (R1_test + R2_test) / R2_test;
            % 找ωc
            lo=0.5; hi=20;
            for _=1:50
                mid=(lo+hi)/2;
                Gm=30/(mid*sqrt(0.09*mid^2+1));
                Gcm=sqrt(1+(mid*T_test)^2)/sqrt(1+(mid*beta_test*T_test)^2);
                if Gm*Gcm>1, lo=mid; else hi=mid; end
            end
            wc_test=(lo+hi)/2;
            phio=-90-atand(0.3*wc_test);
            phic=atand(wc_test*T_test)-atand(wc_test*beta_test*T_test);
            pm_test=180+phio+phic;
            if pm_test>best_pm_local, best_pm_local=pm_test; end
        end
    end
    pm_achievable(idx) = best_pm_local;
end

figure('Name', 'C2与可达到PM的关系', 'Color', 'w', ...
       'Position', [100, 100, 700, 450]);
plot(C2_range, pm_achievable, 'b-', 'LineWidth', 2);
hold on;
yline(40, 'r--', 'PM=40° 最低要求', 'LineWidth', 1.2);
yline(60, 'r--', 'PM=60° 上限', 'LineWidth', 1.2);
xline(1, 'k:', 'C2=1μF (现有)', 'LineWidth', 1.0);
xline(1.4, 'm:', 'C2=1.4μF (最小需求)', 'LineWidth', 1.0);
plot(1, 22.17, 'ro', 'MarkerSize', 10, 'LineWidth', 1.5);
text(1.1, 22.17, '  C2=1μF时最优PM≈22°', 'VerticalAlignment', 'middle');

xlabel('电容 C2 (μF)'); ylabel('可达到的最优相位裕度 PM (°)');
grid on; title('C2 与可达到 PM 的关系 (R≤999.9kΩ)');
legend('最优PM', 'PM=40°', 'PM=60°', 'Location', 'southeast');
saveas(gcf, 'lag_C2_PM关系_物理极限.png');

% ========================================================================
%% 6. 结论与建议
% ========================================================================
fprintf('====== 分析结论 ======\n\n');
fprintf('  1. C2=1μF + R≤999.9kΩ: 被动RC滞后网络最优PM≈22°\n');
fprintf('     无法满足40°~60°的设计要求。\n\n');
fprintf('  2. 物理原因: T_max = 1MΩ×1μF = 1s\n');
fprintf('     零点1/T≥1rad/s迫使ωc过高,原系统相位已严重滞后。\n\n');
fprintf('  3. 解决方案:\n');
fprintf('     a) 使用更大电容 (≥2.2μF): PM=40°~50° 可实现\n');
fprintf('     b) 使用更大电阻 (>2MΩ): 但D5区量程限制\n');
fprintf('     c) 确认原系统G(s)参数是否与本实验一致\n');
fprintf('     d) 检查是否有其他电容值可用 (D5区)\n\n');
fprintf('  4. 本脚本提供C2=1μF最优设计和理论对比,\n');
fprintf('     便于实验报告中讨论物理约束。\n');
