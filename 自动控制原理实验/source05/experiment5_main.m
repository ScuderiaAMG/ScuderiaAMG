%% ============================================================
% 实验5：频率特性法的计算机研究 + 实验4/5综合MATLAB仿真
% MATLAB R2026a
% 华中科技大学 自动化学院 控制理论综合实验
% ============================================================
clear; close all; clc;

fprintf('========================================\n');
fprintf('  实验4-5 MATLAB仿真程序\n');
fprintf('  控制理论综合实验\n');
fprintf('  MATLAB R2026a\n');
fprintf('========================================\n\n');

%% ============================================================
% 实验一：振荡环节在 4K/40K/400K 下的阶跃响应
% 振荡环节传递函数: G(s) = K / (s^2 + 2*zeta*wn*s + wn^2)
% 取 wn=1, zeta=0.5, 改变 K=4,40,400
% ============================================================
fprintf('[实验一] 振荡环节阶跃响应 (K = 4, 40, 400)...\n');

wn1 = 1;
zeta1 = 0.5;
K_values = [4, 40, 400];

figure('Name', '实验一：振荡环节阶跃响应', 'NumberTitle', 'off', ...
       'Position', [100, 100, 900, 600]);

colors = lines(length(K_values));
legend_str = cell(1, length(K_values));

for i = 1:length(K_values)
    K = K_values(i);
    % 开环传递函数: G(s) = K*wn^2/(s^2 + 2*zeta*wn*s + wn^2)
    G = tf(K * wn1^2, [1, 2*zeta1*wn1, wn1^2]);
    % 单位负反馈闭环: T(s) = G(s) / (1 + G(s))
    T = feedback(G, 1);

    % 阶跃响应
    [y, t] = step(T, 10);

    plot(t, y, 'LineWidth', 1.5, 'Color', colors(i,:));
    hold on;
    legend_str{i} = sprintf('K = %d', K);
end

grid on;
xlabel('时间 t (s)', 'FontSize', 12);
ylabel('幅值', 'FontSize', 12);
title('实验一：振荡环节在不同增益下的阶跃响应', 'FontSize', 14);
legend(legend_str, 'Location', 'best', 'FontSize', 10);
saveas(gcf, '实验一_振荡环节阶跃响应.png');

% 打印性能指标
fprintf('\n--- 实验一：性能指标 ---\n');
for i = 1:length(K_values)
    K = K_values(i);
    G = tf(K * wn1^2, [1, 2*zeta1*wn1, wn1^2]);
    T = feedback(G, 1);
    info = stepinfo(T);
    fprintf('K = %3d: 超调量 σ = %5.1f%%, 调节时间 ts = %.3f s, ', ...
            K, info.Overshoot, info.SettlingTime);
    fprintf('峰值时间 tp = %.3f s, 上升时间 tr = %.3f s\n', ...
            info.PeakTime, info.RiseTime);
end
fprintf('\n');

%% ============================================================
% 实验二 第一部分：二阶系统不同阻尼比下的阶跃响应
% 二阶系统闭环传递函数:
%   T(s) = wn^2 / (s^2 + 2*zeta*wn*s + wn^2)
% 根据指导书，α = {0, 0.13, 0.33, 0.44, 0.63}
% 对应不同阻尼比，wn = 10 rad/s (来自 K3=10 的电路参数)
% ============================================================
fprintf('[实验二-1] 二阶系统不同阻尼比下的阶跃响应...\n');

wn2 = 10;                         % 无阻尼自然频率 (rad/s)
alpha_values = [0, 0.13, 0.33, 0.44, 0.63];
% 阻尼比 zeta 与 α 的关系: zeta = alpha * K3 / (2*wn)
% K3 = 10 为放大器增益，简化取 zeta ≈ alpha * 2
zeta_values = alpha_values * 2;   % 对应: 0, 0.26, 0.66, 0.88, 1.26

figure('Name', '实验二-1：不同阻尼比阶跃响应', 'NumberTitle', 'off', ...
       'Position', [100, 100, 900, 600]);

legend_str2 = cell(1, length(alpha_values));

for i = 1:length(alpha_values)
    z = zeta_values(i);
    T = tf(wn2^2, [1, 2*z*wn2, wn2^2]);
    [y, t] = step(T, 3);
    plot(t, y, 'LineWidth', 1.5);
    hold on;
    legend_str2{i} = sprintf('\\alpha = %.2f (\\zeta = %.2f)', ...
                             alpha_values(i), z);
end

grid on;
xlabel('时间 t (s)', 'FontSize', 12);
ylabel('幅值', 'FontSize', 12);
title('实验二-1：二阶系统在不同阻尼比下的阶跃响应', 'FontSize', 14);
legend(legend_str2, 'Location', 'best', 'FontSize', 9);
saveas(gcf, '实验二_1_阻尼比阶跃响应.png');

% 打印瞬态响应指标表
fprintf('\n--- 实验二-1：瞬态响应指标表 ---\n');
fprintf('  α      ζ       ωn(rad/s)  ωd(rad/s)  σ%%     tp(s)    ts(s)\n');
fprintf('-----------------------------------------------------------------\n');
for i = 1:length(alpha_values)
    z = zeta_values(i);
    T = tf(wn2^2, [1, 2*z*wn2, wn2^2]);
    info = stepinfo(T);

    if z < 1
        wd = wn2 * sqrt(1 - z^2);
    else
        wd = 0;
    end
    fprintf('  %.2f   %.2f     %.1f        %.3f      ', ...
            alpha_values(i), z, wn2, wd);
    if info.Overshoot > 0
        fprintf('%5.1f   %.4f   %.4f\n', info.Overshoot, info.PeakTime, info.SettlingTime);
    else
        fprintf('  --     --     %.4f\n', info.SettlingTime);
    end
end
fprintf('\n');

%% ============================================================
% 实验二 第二部分：0型、I型系统的稳态误差
%
% 0型系统: G(s) = K / (Ts + 1)        → 对阶跃输入 ess = 1/(1+K)
% I型系统: G(s) = K / [s(Ts + 1)]     → 对阶跃输入 ess = 0
%                                        对斜坡输入 ess = 1/K
% II型系统: G(s) = K / [s^2(Ts + 1)]  → 对阶跃/斜坡 ess = 0
% ============================================================
fprintf('[实验二-2] 0型/I型/II型系统稳态误差分析...\n');

T_const = 1;        % 时间常数
K_vals_02 = [10, 20];  % 不同增益

% --- 0型系统 ---
figure('Name', '实验二-2：0型系统', 'NumberTitle', 'off', ...
       'Position', [100, 100, 900, 400]);

for sp = 1:2
    subplot(1, 2, sp);
    K = K_vals_02(sp);
    G0 = tf(K, [T_const, 1]);
    T0 = feedback(G0, 1);

    [y, t] = step(T0, 5);
    plot(t, y, 'LineWidth', 1.5, 'Color', colors(sp,:));
    hold on;
    yline(1, 'k--');
    yline(K/(1+K), 'r--', 'LineWidth', 1);
    grid on;
    xlabel('时间 t (s)');
    ylabel('幅值');
    title(sprintf('0型系统 K=%d (e_{ss}=%.3f)', K, 1/(1+K)));
end
sgtitle('实验二-2：0型系统阶跃响应与稳态误差');
saveas(gcf, '实验二_2_0型系统.png');

% --- I型系统 ---
figure('Name', '实验二-2：I型系统', 'NumberTitle', 'off', ...
       'Position', [100, 100, 900, 600]);

for sp = 1:2
    K = K_vals_02(sp);
    G1 = tf(K, [T_const, 1, 0]);  % 分母包含 s
    T1 = feedback(G1, 1);

    % 阶跃响应
    subplot(2, 2, sp);
    [y, t] = step(T1, 5);
    plot(t, y, 'LineWidth', 1.5, 'Color', colors(sp,:));
    hold on; yline(1, 'k--');
    grid on;
    xlabel('时间 t (s)'); ylabel('幅值');
    title(sprintf('I型系统 K=%d 阶跃响应 (e_{ss}=0)', K));

    % 斜坡响应
    subplot(2, 2, sp+2);
    t = 0:0.01:5;
    u = t;                          % 单位斜坡输入
    [y, ~] = lsim(T1, u, t);
    plot(t, y, 'LineWidth', 1.5, 'Color', colors(sp,:));
    hold on;
    plot(t, t - 1/K, 'r--', 'LineWidth', 1);  % 稳态跟踪（滞后1/K）
    grid on;
    xlabel('时间 t (s)'); ylabel('幅值');
    title(sprintf('I型系统 K=%d 斜坡响应 (e_{ss}=%.3f)', K, 1/K));
end
sgtitle('实验二-2：I型系统阶跃与斜坡响应');
saveas(gcf, '实验二_2_I型系统.png');

% --- II型系统 ---
fprintf('  II型系统: 对阶跃和斜坡输入的稳态误差均为 0\n');
G2 = tf(K_vals_02(1), [T_const, 1, 0, 0]);  % 分母包含 s^2
T2 = feedback(G2, 1);
figure('Name', '实验二-2：II型系统', 'NumberTitle', 'off');
subplot(1,2,1); step(T2, 5); grid on;
title(sprintf('II型系统 K=%d 阶跃响应', K_vals_02(1)));
subplot(1,2,2);
t = 0:0.01:5;
[y, ~] = lsim(T2, t, t);
plot(t, y, 'LineWidth', 1.5); hold on; plot(t, t, 'r--');
grid on; xlabel('时间 t (s)'); ylabel('幅值');
title('II型系统斜坡响应');
saveas(gcf, '实验二_2_II型系统.png');

%% ============================================================
% 实验三：高阶系统（三阶I型）的稳定性分析
% 传递函数: G(s) = K / [s(T1*s + 1)(T2*s + 1)]
% 通过劳斯判据求临界增益 Kc
% ============================================================
fprintf('[实验三] 高阶系统稳定性分析...\n');

T1 = 0.1;  T2 = 0.2;  T3 = 0.05;  % 时间常数

% 三阶I型系统: G(s) = K / [s * (T1*s+1) * (T2*s+1)]
% 特征方程: T1*T2*s^3 + (T1+T2)*s^2 + s + K = 0
% 劳斯表:
%   s^3 | T1*T2        1
%   s^2 | T1+T2        K
%   s^1 | (T1+T2 - T1*T2*K)/(T1+T2)   0
%   s^0 | K
% 临界稳定条件: (T1+T2) - T1*T2*Kc = 0
%  => Kc = (T1+T2) / (T1*T2)

Kc = (T1 + T2) / (T1 * T2);
fprintf('  特征方程: %.3f s^3 + %.3f s^2 + s + K = 0\n', T1*T2, T1+T2);
fprintf('  临界增益 Kc = %.2f\n', Kc);

% 三种状态
K_stable = Kc * 0.5;      % 稳定
K_critical = Kc;           % 临界稳定
K_unstable = Kc * 1.5;    % 不稳定

K_states = [K_stable, K_critical, K_unstable];
state_names = {'稳定 (K < Kc)', '临界稳定 (K = Kc)', '不稳定 (K > Kc)'};

figure('Name', '实验三：三阶系统稳定性', 'NumberTitle', 'off', ...
       'Position', [100, 100, 1100, 800]);

for i = 1:3
    K = K_states(i);
    % 开环: G = K / [s(T1*s+1)(T2*s+1)]
    G3 = tf(K, [T1*T2, T1+T2, 1, 0]);
    T3_cl = feedback(G3, 1);

    % 阶跃响应
    subplot(3, 2, 2*i-1);
    step(T3_cl, 10);
    grid on;
    title(sprintf('阶跃响应 (%s, K=%.2f)', state_names{i}, K));

    % 频率特性 (Bode)
    subplot(3, 2, 2*i);
    margin(G3);
    title(sprintf('Bode图 (%s, K=%.2f)', state_names{i}, K));
end
sgtitle('实验三：高阶系统稳定性分析', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, '实验三_高阶系统稳定性.png');

% 参数变化影响 - 不同时间常数
figure('Name', '实验三：参数变化影响', 'NumberTitle', 'off');
T2_variations = [0.1, 0.2, 0.3, 0.5];
for i = 1:4
    T2_var = T2_variations(i);
    Kc_var = (T1 + T2_var) / (T1 * T2_var);
    G_var = tf(Kc_var * 0.8, [T1*T2_var, T1+T2_var, 1, 0]);
    T_var = feedback(G_var, 1);
    subplot(2, 2, i);
    step(T_var, 6);
    grid on;
    title(sprintf('T_2=%.1f, K_c=%.1f, K=%.1f(稳定)', T2_var, Kc_var, Kc_var*0.8));
end
sgtitle('实验三：时间常数变化对稳定性的影响');
saveas(gcf, '实验三_参数变化影响.png');

fprintf('\n');

%% ============================================================
% 自选题1：频率特性响应和根轨迹分析（自动化专业必做）
% 10个传递函数
% ============================================================
fprintf('[自选题1] 10个传递函数的频率特性和根轨迹分析...\n');

% 定义10个开环传递函数
G_cell = {
    tf(2, conv([1, 1], [1, 1, 1])),          ...  % 1
    tf(1, conv([0.8, 1], [1, 1, 1])),         ...  % 2
    tf(2, conv([1, 1], [1, 0.8, 1])),         ...  % 3
    tf(2, conv([1, 1], [1, 1.2, 1])),         ...  % 4
    tf(2, conv([1.2, 1], [1, 1, 1])),         ...  % 5
    tf(2, conv([2, 1], [1, 1, 1])),           ...  % 6
    tf(2, conv([1, 1], [1, 2, 1])),           ...  % 7
    tf(2, conv([0.6, 1], [1, 1.2, 1])),       ...  % 8
    tf(2, conv([5, 1], [1, 1, 1])),           ...  % 9
    tf(2, conv([4, 1], [1, 0.75, 1]))         ...  % 10
};

% --- 根轨迹图 ---
figure('Name', '自选题1：根轨迹', 'NumberTitle', 'off', ...
       'Position', [50, 50, 1400, 900]);

for i = 1:10
    subplot(3, 4, i);
    rlocus(G_cell{i});
    grid on;
    title(sprintf('G_%d(s)', i), 'FontSize', 9);
end
sgtitle('自选题1：10个传递函数的根轨迹图', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, '自选题1_根轨迹汇总.png');

% --- Bode 图 ---
figure('Name', '自选题1：Bode图', 'NumberTitle', 'off', ...
       'Position', [50, 50, 1400, 900]);

for i = 1:10
    subplot(3, 4, i);
    [Gm, Pm, Wcg, Wcp] = margin(G_cell{i});
    margin(G_cell{i});
    grid on;
    title(sprintf('G_%d: Gm=%.1fdB, Pm=%.1f°', i, ...
                  20*log10(Gm), Pm), 'FontSize', 8);
end
sgtitle('自选题1：10个传递函数的Bode图', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, '自选题1_Bode图汇总.png');

% --- 阶跃响应汇总 (闭环) ---
figure('Name', '自选题1：闭环阶跃响应', 'NumberTitle', 'off', ...
       'Position', [50, 50, 1400, 900]);

for i = 1:10
    subplot(3, 4, i);
    T = feedback(G_cell{i}, 1);
    step(T, 15);
    grid on;
    info = stepinfo(T);
    title(sprintf('G_%d: σ=%.1f%%, t_s=%.2fs', i, info.Overshoot, info.SettlingTime), ...
          'FontSize', 8);
end
sgtitle('自选题1：10个传递函数的闭环阶跃响应', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, '自选题1_阶跃响应汇总.png');

% 打印频率特性指标表
fprintf('\n--- 自选题1：频率特性与性能指标汇总 ---\n');
fprintf('编号  Gm(dB)   Pm(deg)   Wcg(rad/s)  Wcp(rad/s)  σ%%      ts(s)\n');
fprintf('-----------------------------------------------------------------\n');
for i = 1:10
    [Gm, Pm, Wcg, Wcp] = margin(G_cell{i});
    T = feedback(G_cell{i}, 1);
    info = stepinfo(T);
    fprintf('G_%2d   %6.2f   %6.1f    %7.3f     %7.3f    %6.1f   %6.2f\n', ...
            i, 20*log10(Gm), Pm, Wcg, Wcp, info.Overshoot, info.SettlingTime);
end
fprintf('\n');

%% ============================================================
% 自选题2：离散系统阶跃响应分析（人工智能专业必做）
% 对连续系统进行离散化，分析阶跃响应
% ============================================================
fprintf('[自选题2] 离散系统阶跃响应分析...\n');

Ts_values = [0.01, 0.05, 0.1, 0.2, 0.5];  % 不同采样周期

figure('Name', '自选题2：离散系统阶跃响应', 'NumberTitle', 'off', ...
       'Position', [100, 100, 900, 600]);

legend_disc = cell(1, length(Ts_values) + 1);

% 连续系统作为参考（使用 G1: 2/[(s+1)(s^2+s+1)]）
G_cont = tf(2, conv([1, 1], [1, 1, 1]));
T_cont = feedback(G_cont, 1);
[y_cont, t_cont] = step(T_cont, 15);
stairs(t_cont, y_cont, 'k-', 'LineWidth', 2);
hold on;
legend_disc{1} = '连续系统';

for i = 1:length(Ts_values)
    Ts = Ts_values(i);
    % 零阶保持器离散化
    Gd = c2d(G_cont, Ts, 'zoh');
    Td = feedback(Gd, 1);
    [yd, td] = step(Td, 15);
    stairs(td, yd, 'LineWidth', 1.2);
    legend_disc{i+1} = sprintf('离散 Ts=%.2f', Ts);
end

grid on;
xlabel('时间 t (s)', 'FontSize', 12);
ylabel('幅值', 'FontSize', 12);
title('自选题2：不同采样周期下的离散系统阶跃响应', 'FontSize', 14);
legend(legend_disc, 'Location', 'best', 'FontSize', 9);
saveas(gcf, '自选题2_离散系统阶跃响应.png');

% 估读超调量和调节时间
fprintf('\n--- 自选题2：离散系统性能指标估读 ---\n');
fprintf('  采样周期Ts   超调量σ%%    调节时间ts(s)\n');
fprintf('-------------------------------------------\n');
fprintf('  连续系统     ');
T_cont = feedback(G_cont, 1);
info_cont = stepinfo(T_cont);
fprintf('  %6.1f        %6.2f\n', info_cont.Overshoot, info_cont.SettlingTime);

for i = 1:length(Ts_values)
    Ts = Ts_values(i);
    Gd = c2d(G_cont, Ts, 'zoh');
    Td = feedback(Gd, 1);
    info_d = stepinfo(Td);
    fprintf('  Ts=%.2f        %6.1f        %6.2f\n', Ts, info_d.Overshoot, info_d.SettlingTime);
end
fprintf('\n');

% --- 离散频率特性对比 ---
figure('Name', '自选题2：离散与连续频率特性对比', 'NumberTitle', 'off', ...
       'Position', [100, 100, 900, 600]);

bode(G_cont, 'k-', 'LineWidth', 2);
hold on;
for i = 1:3
    Ts = Ts_values(i);
    Gd = c2d(G_cont, Ts, 'zoh');
    % 离散Bode通过dbode或转换回连续近似
    [mag, phase, w] = bode(Gd);
    mag_db = 20*log10(squeeze(mag));
    phase_deg = squeeze(phase);
    semilogx(w, mag_db, 'LineWidth', 1);
end
grid on;
legend(['连续', arrayfun(@(x) sprintf('Ts=%.2f', x), Ts_values(1:3), 'UniformOutput', false)]);
title('自选题2：离散与连续系统频率特性对比');
saveas(gcf, '自选题2_离散频率特性.png');

%% ============================================================
% 附加：使用 Control System Designer 的说明
% ============================================================
fprintf('========================================\n');
fprintf('  全部实验完成！生成图像文件:\n');
fprintf('    实验一_振荡环节阶跃响应.png\n');
fprintf('    实验二_1_阻尼比阶跃响应.png\n');
fprintf('    实验二_2_0型系统.png\n');
fprintf('    实验二_2_I型系统.png\n');
fprintf('    实验二_2_II型系统.png\n');
fprintf('    实验三_高阶系统稳定性.png\n');
fprintf('    实验三_参数变化影响.png\n');
fprintf('    自选题1_根轨迹汇总.png\n');
fprintf('    自选题1_Bode图汇总.png\n');
fprintf('    自选题1_阶跃响应汇总.png\n');
fprintf('    自选题2_离散系统阶跃响应.png\n');
fprintf('    自选题2_离散频率特性.png\n');
fprintf('\n');
fprintf('  交互式工具: 在命令窗口输入 controlSystemDesigner 打开GUI\n');
fprintf('  根轨迹工具: 在命令窗口输入 rltool 打开根轨迹设计器\n');
fprintf('========================================\n');
