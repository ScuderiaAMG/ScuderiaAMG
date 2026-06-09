% 1. 定义原系统
num = 30;
den = [0.3, 1, 0];
sys_open = tf(num, den);

% 2. 设定极其精确的目标相位裕度
gamma_target = 54.69; 

% 3. 严格针对"无源网络衰减"的联立方程求解
% 在无源网络下，新剪切频率 Wc_new 必定小于原穿越频率 (9.726 rad/s)
% Wc_new 处的原系统幅值需等于 sqrt(alpha)
fun = @(w) abs( -90 - atand(0.3*w) + asind( ( (30/(w*sqrt(0.09*w^2+1)))^2 - 1 ) / ( (30/(w*sqrt(0.09*w^2+1)))^2 + 1 ) ) - (gamma_target - 180) );

% 在 1 到 9.7 rad/s 之间寻找最优解
Wc_new = fminbnd(fun, 1, 9.7); 

% 4. 重新计算真实的物理参数
mag_original = 30 / (Wc_new * sqrt(0.09 * Wc_new^2 + 1));
alpha = mag_original^2;  % 核心修正：纯无源网络下的 alpha 定义
T = 1 / (Wc_new * sqrt(alpha));

% 计算具体元件阻值 (假定 C1 = 1uF)
C1 = 1e-6; 
R4 = alpha * T / C1;
R5 = R4 / (alpha - 1);

% 5. 构建严格的无源校正环节传递函数并验证
num_c = [alpha*T, 1];
den_c = [T, 1];
sys_c = tf(num_c, den_c) / alpha; % 真实包含无源衰减

sys_compensated = sys_open * sys_c;
[Gm_new, Pm_new, Wcg_new, Wcp_new] = margin(sys_compensated);

fprintf('\n=== 修正版无源超前校正精确设计 ===\n');
fprintf('设定目标相位裕度: %.2f 度\n', gamma_target);
fprintf('实际验证相位裕度: %.2f 度 (解决 63.5° 误差问题)\n', Pm_new);
fprintf('校正后真实剪切频率: %.2f rad/s\n', Wcp_new);
fprintf('超前系数 alpha: %.3f\n', alpha);
fprintf('---------------------------------\n');
fprintf('★ 请将 R4 调节至: %.1f kOhm\n', R4 / 1000);
fprintf('★ 请将 R5 调节至: %.1f kOhm\n', R5 / 1000);
fprintf('===================================\n');

% 绘制对比图
figure('Name', '无源超前校正严格验证', 'Color', 'w');
margin(sys_open);
hold on;
margin(sys_compensated);
grid on;
legend('校正前原系统', '校正后系统 (包含无源衰减)');
title('频域法无源串联超前校正精确验证');