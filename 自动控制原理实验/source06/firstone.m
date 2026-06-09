num = 30;
den = [0.3, 1, 0]; 
sys_open = tf(num, den);

figure('Name', '修正后的原系统频率特性分析', 'Color', 'w');
margin(sys_open);
grid on;
title('原系统开环Bode图与稳定性裕度 (R3=300k\Omega)');

[Gm, Pm, Wcg, Wcp] = margin(sys_open);

fprintf('\n====== 修正后原系统频率特性计算结果 ======\n');
fprintf('剪切频率 (幅值穿越频率 Wcp): %.3f rad/s\n', Wcp);
fprintf('相位裕度 (PM): %.2f 度\n', Pm);

if isinf(Gm)
    fprintf('幅值裕度 (GM): 无穷大 (相频曲线未穿过-180度，系统绝对稳定)\n');
else
    fprintf('幅值裕度 (GM): %.2f dB\n', 20*log10(Gm));
    fprintf('相位穿越频率 (Wcg): %.2f rad/s\n', Wcg);
end
fprintf('==========================================\n');

sys_closed = feedback(sys_open, 1);
figure('Name', '原系统闭环阶跃响应', 'Color', 'w');
step(sys_closed); 
grid on;
title('理论闭环单位阶跃响应 (验证高超调量)');