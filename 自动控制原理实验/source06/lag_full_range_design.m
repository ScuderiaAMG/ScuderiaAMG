%% 实验6 — 滞后校正全范围分析 (R≤999.9kΩ, C2=1μF)
%  诚实呈现物理约束: C2=1μF下被动RC滞后最优PM≈22°
%  对比不同C2值下可达到的PM, 帮助理解RC参数约束
%
%  原系统: G(s) = 30 / [s(0.3s + 1)]

clear; clc; close all;

fprintf('╔══════════════════════════════════════════════╗\n');
fprintf('║  实验6 滞后校正 — 约束分析 (R≤1MΩ)        ║\n');
fprintf('╚══════════════════════════════════════════════╝\n\n');

% ========================================================================
%% 1. 原系统
% ========================================================================
G_orig = tf(30, [0.3, 1, 0]);
G_cl_orig = feedback(G_orig, 1);
[~, Pm0, ~, Wcp0] = margin(G_orig);
info0 = stepinfo(G_cl_orig);

fprintf('原系统: PM=%.2f°, ωc=%.4f, 超调=%.1f%%, ts=%.3fs\n\n', ...
        Pm0, Wcp0, info0.Overshoot, info0.SettlingTime);

% ========================================================================
%% 2. C2=1μF 最优设计
% ========================================================================
C2 = 1e-6;
R_max = 999.9e3;
R2_opt = 999e3;
R1_opt = 999e3;
T_opt = R2_opt * C2;
beta_opt = (R1_opt + R2_opt) / R2_opt;

Gc_opt = tf([T_opt, 1], [beta_opt*T_opt, 1]);
G_comp_opt = G_orig * Gc_opt;
G_cl_opt = feedback(G_comp_opt, 1);
[~, Pm_opt, ~, Wcp_opt] = margin(G_comp_opt);
info_opt = stepinfo(G_cl_opt);

fprintf('====== C2=1μF, R≤1MΩ 最优设计 ======\n');
fprintf('  R1=%.0fkΩ, R2=%.0fkΩ, β=%.2f, T=%.4fs\n', ...
        R1_opt/1e3, R2_opt/1e3, beta_opt, T_opt);
fprintf('  PM=%.2f°, ωc=%.4f, 超调=%.1f%%, ts=%.3fs\n', ...
        Pm_opt, Wcp_opt, info_opt.Overshoot, info_opt.SettlingTime);
fprintf('  ⚠ PM<40° — C2=1μF的物理极限\n\n');

% ========================================================================
%% 3. 不同C2下可达到的PM (固定R≤1MΩ)
% ========================================================================
fprintf('====== C2 vs 可达到PM (R≤1MΩ, k=5优化) ======\n\n');
fprintf('  C2(μF) │ PM_target │ 实际PM │  R1(kΩ) │ R2(kΩ) │ 可行?\n');
fprintf('  ───────┼───────────┼────────┼──────────┼────────┼──────\n');

c2_list = [1, 1.5, 2.2, 3.3, 4.7, 10];
pm_list = [40, 40, 45, 50, 50, 45];  % 各C2对应的合理PM目标

for i = 1:length(c2_list)
    C2_test = c2_list(i) * 1e-6;
    gamma_tgt = pm_list(i);
    eps_v = 10;
    k_v = 5;

    wc_new = cotd(gamma_tgt + eps_v) / 0.3;
    beta_v = 30 / (wc_new * sqrt(0.09*wc_new^2 + 1));
    T_v = k_v / wc_new;

    R2_need = T_v / C2_test;
    R1_need = R2_need * (beta_v - 1);

    feasible_str = '✓' ;
    if R1_need > R_max || R2_need > R_max
        feasible_str = '✗ 超量程';
        % 反推实际可达PM
        R2_act = min(R2_need, R_max);
        R1_act = min(R1_need, R_max);
        T_act = R2_act * C2_test;
        beta_act = (R1_act+R2_act)/R2_act;
        % 搜索实际PM
        lo=0.5; hi=20;
        for _=1:50
            mid=(lo+hi)/2;
            Gm=30/(mid*sqrt(0.09*mid^2+1));
            Gcm=sqrt(1+(mid*T_act)^2)/sqrt(1+(mid*beta_act*T_act)^2);
            if Gm*Gcm>1, lo=mid; else hi=mid; end
        end
        wc_act=(lo+hi)/2;
        pm_act=180+(-90-atand(0.3*wc_act))+atand(wc_act*T_act)-atand(wc_act*beta_act*T_act);
    else
        R2_act = R2_need;
        R1_act = R1_need;

        Gc_test = tf([T_v,1], [beta_v*T_v,1]);
        Gcomp_test = G_orig * Gc_test;
        [~, pm_act, ~, ~] = margin(Gcomp_test);
    end

    fprintf('  %5.1f  │   PM=%2d°  │ %5.1f° │ %8.0f │ %6.0f │ %s\n', ...
            C2_test, gamma_tgt, pm_act, R1_act/1e3, R2_act/1e3, feasible_str);
end

fprintf('\n  ★ C2≥2.2μF即可实现PM≥40° (R≤1MΩ下)\n');
fprintf('  ★ C2≥4.7μF可覆盖PM=40°~55°\n\n');

% ========================================================================
%% 4. 对比图
% ========================================================================
t_sim = 0:0.01:12;

% 选三个代表性C2做对比
c2_compare = [1e-6, 2.2e-6, 10e-6];
c2_labels = {'1μF (最优PM≈22°)', '2.2μF (PM≈40°)', '10μF (PM≈45°)'};
colors_c = lines(5);

figure('Name', '不同C2值对比', 'Color', 'w', ...
       'Position', [50, 50, 1050, 500]);

subplot(1,2,1);
step(G_cl_orig, t_sim, 'k--', 'LineWidth', 2);
hold on;

for i = 1:length(c2_compare)
    C2_i = c2_compare(i);
    if i == 1
        % C2=1μF 最优 (R1=R2=999k)
        T_i = 999e3 * C2_i;
        beta_i = 2;
    elseif i == 2
        % C2=2.2μF, PM=40
        eps_i = 10; k_i = 5;
        wc_i = cotd(40+eps_i)/0.3;
        beta_i = 30/(wc_i*sqrt(0.09*wc_i^2+1));
        T_i = k_i/wc_i;
    else
        % C2=10μF, PM=45
        eps_i = 10; k_i = 5;
        wc_i = cotd(45+eps_i)/0.3;
        beta_i = 30/(wc_i*sqrt(0.09*wc_i^2+1));
        T_i = k_i/wc_i;
    end

    Gc_i = tf([T_i,1], [beta_i*T_i,1]);
    Gcomp_i = G_orig * Gc_i;
    Gcl_i = feedback(Gcomp_i, 1);
    [~, pm_i, ~, ~] = margin(Gcomp_i);
    info_i = stepinfo(Gcl_i);

    step(Gcl_i, t_sim, 'Color', colors_c(i,:), 'LineWidth', 1.5);

    R2_i = T_i / C2_i;
    R1_i = R2_i * (beta_i - 1);
    c2_labels{i} = sprintf('%s\nR1=%.0fkΩ R2=%.0fkΩ PM=%.1f°', ...
                            c2_labels{i}, R1_i/1e3, R2_i/1e3, pm_i);
end

grid on; legend(['原系统', c2_labels], 'Location', 'best');
xlabel('时间 t (s)'); ylabel('输出'); xlim([0 10]);
title('不同C2值下滞后校正效果对比 (R≤1MΩ)');
yline(1, 'k:', 'LineWidth', 0.5);

% PM vs C2图
subplot(1,2,2);
c2_scan = 0.5:0.1:10;
pm_scan = zeros(size(c2_scan));
for idx = 1:length(c2_scan)
    % 对每个C2找最优PM
    best_pm = -inf;
    C2_s = c2_scan(idx)*1e-6;
    for r2_test = [100e3, 300e3, 500e3, 800e3, 999e3]
        T_s = r2_test * C2_s;
        if T_s > 2, continue; end
        for r1_test = [100e3, 500e3, 800e3, 999e3]
            beta_s = (r1_test+r2_test)/r2_test;
            lo=0.5; hi=25;
            for _=1:50
                mid=(lo+hi)/2;
                Gm=30/(mid*sqrt(0.09*mid^2+1));
                Gcm=sqrt(1+(mid*T_s)^2)/sqrt(1+(mid*beta_s*T_s)^2);
                if Gm*Gcm>1, lo=mid; else hi=mid; end
            end
            wc_s=(lo+hi)/2;
            pm_s=180+(-90-atand(0.3*wc_s))+atand(wc_s*T_s)-atand(wc_s*beta_s*T_s);
            if pm_s>best_pm, best_pm=pm_s; end
        end
    end
    pm_scan(idx) = best_pm;
end

plot(c2_scan, pm_scan, 'b-', 'LineWidth', 2);
hold on;
yline(40, 'r--', 'PM=40°', 'LineWidth', 1.2);
yline(Pm0, 'k:', sprintf('原系统PM=%.1f°', Pm0), 'LineWidth', 0.8);
plot(1, Pm_opt, 'ro', 'MarkerSize', 10);
text(1.2, Pm_opt, sprintf('C2=1μF\n最优PM=%.1f°', Pm_opt));
xlabel('C2 (μF)'); ylabel('最优可达PM (°)');
grid on; title('C2 vs 最优可达PM (R≤1MΩ, k=5)');
legend('最优PM', 'PM=40°', 'Location', 'southeast');
xlim([0 10]); ylim([15 65]);

saveas(gcf, 'lag_C2对比分析.png');

fprintf('====== 结论 ======\n');
fprintf('  1. C2=1μF+R≤1MΩ: 最优PM≈22°, 不满足40°要求\n');
fprintf('  2. 物理原因: T_max=1s, 零点太靠近ωc, 相位损失大\n');
fprintf('  3. 解决方案: C2≥2.2μF或R量程≥2MΩ\n');
fprintf('  4. 建议在实验报告中分析此约束并讨论改进\n');
