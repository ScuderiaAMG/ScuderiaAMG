clear; clc; close all;

num_open = 30;
den_open = [0.3, 1, 0];
sys_open = tf(num_open, den_open);

R4 = 240000; % 实际选用 R4 = 240 kOhm
R5 = 120000; % 实际选用 R5 = 120 kOhm
C1 = 1e-6;   % C1 = 1 uF

alpha = (R4 + R5) / R5;  % 超前系数 (此时应为 3)
T = R4 * C1 / alpha;     % 时间常数 (此时应为 0.08 s)

num_c = [alpha * T, 1];
den_c = [T, 1];
sys_c = tf(num_c, den_c) / alpha; 

%% 4. 计算校正后的开环传递函数
sys_comp = sys_open * sys_c;

%% 5. 计算并打印频率特性指标
[Gm_old, Pm_old, Wcg_old, Wcp_old] = margin(sys_open);
[Gm_comp, Pm_comp, Wcg_comp, Wcp_comp] = margin(sys_comp);

fprintf('\n====== 实际硬件参数验证结果 ======\n');
fprintf('实际采用阻值: R4 = %d kOhm, R5 = %d kOhm\n', R4/1000, R5/1000);
fprintf('超前系数 alpha: %d\n', alpha);
fprintf('----------------------------------\n');
fprintf('[校正前] 剪切频率 Wc: %.3f rad/s, 相位裕度 PM: %.2f 度\n', Wcp_old, Pm_old);
fprintf('[校正后] 剪切频率 Wc: %.3f rad/s, 相位裕度 PM: %.2f 度\n', Wcp_comp, Pm_comp);
fprintf('==================================\n\n');

%% 6. 绘图 1：开环 Bode 图对比
figure('Name', '超前校正前后频率特性对比 (Bode 图)', 'Color', 'w');
margin(sys_open);
hold on;
margin(sys_comp);
grid on;
legend('校正前 (原系统)', '校正后 (实际参数R4=240k, R5=120k)', 'Location', 'southwest');
title('频率特性法无源串联超前校正');

sys_closed_open = feedback(sys_open, 1);
sys_closed_comp = feedback(sys_comp, 1);

figure('Name', '采用实际参数的阶跃响应对比', 'Color', 'w');
t = 0:0.01:4; 
step(sys_closed_open, t, 'b--'); % 蓝色虚线表示校正前
hold on;
step(sys_closed_comp, t, 'r', 'LineWidth', 1.5); % 红色实线加粗表示校正后
grid on;

legend('校正前 (剧烈震荡)', '校正后 (平稳收敛)', 'Location', 'northeast');
title('超前校正对闭环系统动态性能的改善');
xlabel('时间 (秒)');
ylabel('输出幅值 (V)');