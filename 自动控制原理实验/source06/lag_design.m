%% 实验6 — 滞后校正设计函数 (支持约束分析)
%  result = lag_design(gamma_target, R1_max, R2_max, C2_val)
%
%  输入:
%    gamma_target - 目标相位裕度 (°), 范围 40~60
%    R1_max, R2_max - 电阻上限 (Ω), 默认 999.9e3
%    C2_val       - 电容值 (F), 默认 1e-6
%
%  输出 result 结构体:
%    .feasible       - 是否可行 (true/false)
%    .Pm_achieved    - 实际可达到的PM
%    .best_R1, .best_R2 - 最优电阻值
%    .C2_required    - 若不可行, 给出所需最小C2
%    .Gc, .G_comp    - 校正网络和校正后系统
%
%  使用示例:
%    r = lag_design(45);                    % PM=45°, 默认约束
%    r = lag_design(45, 500e3, 500e3, 1e-6); % 更严格约束

function result = lag_design(gamma_target, R1_max, R2_max, C2_val)
    if nargin < 2, R1_max = 999.9e3; end
    if nargin < 3, R2_max = 999.9e3; end
    if nargin < 4, C2_val = 1e-6;       end

    % 原系统
    G_orig = tf(30, [0.3, 1, 0]);
    [~, Pm0, ~, Wcp0] = margin(G_orig);
    info0 = stepinfo(feedback(G_orig, 1));

    % --- 数值搜索最优设计 ---
    best_pm = -inf;
    best_params = [];

    R2_list = unique([round(R2_max), round(R2_max*0.8), round(R2_max*0.5), ...
                      round(R2_max*0.3), round(R2_max*0.1)]);
    R1_list = unique([round(R1_max), round(R1_max*0.8), round(R1_max*0.5), ...
                      round(R1_max*0.3), round(R1_max*0.1)]);

    for r2 = R2_list
        T_v = r2 * C2_val;
        if T_v <= 0, continue; end
        for r1 = R1_list
            if r1 + r2 > (R1_max + R2_max), continue; end
            beta_v = (r1 + r2) / r2;

            % 二分法求ωc
            lo = 0.1; hi = 30;
            for iter = 1:60
                mid = (lo + hi) / 2;
                Gm = 30 / (mid * sqrt(0.09*mid^2 + 1));
                Gcm = sqrt(1 + (mid*T_v)^2) / sqrt(1 + (mid*beta_v*T_v)^2);
                if Gm * Gcm > 1, lo = mid; else hi = mid; end
            end
            wc_v = (lo + hi) / 2;

            phio = -90 - atand(0.3 * wc_v);
            phic = atand(wc_v * T_v) - atand(wc_v * beta_v * T_v);
            pm_v = 180 + phio + phic;

            if pm_v > best_pm
                best_pm = pm_v;
                best_params = struct('R1', r1, 'R2', r2, 'T', T_v, ...
                    'beta', beta_v, 'wc', wc_v, 'Pm', pm_v, ...
                    'phi_c', phic, 'phi_orig', phio);
            end
        end
    end

    % --- 构建结果 ---
    feasible = (best_pm >= gamma_target - 2);  % ±2°容忍

    if feasible
        % 可行: 使用搜索到的最优参数
        bp = best_params;
        Gc = tf([bp.T, 1], [bp.beta * bp.T, 1]);
        G_comp = G_orig * Gc;
        G_cl = feedback(G_comp, 1);
        info_cl = stepinfo(G_cl);

        result = struct(...
            'feasible', true, ...
            'gamma_target', gamma_target, ...
            'Pm_achieved', bp.Pm, ...
            'Pm_original', Pm0, ...
            'best_R1', bp.R1, 'best_R2', bp.R2, ...
            'T', bp.T, 'beta', bp.beta, 'wc', bp.wc, ...
            'Gc', Gc, 'G_comp', G_comp, 'G_cl', G_cl, ...
            'overshoot', info_cl.Overshoot, ...
            'settling_time', info_cl.SettlingTime);

        fprintf('\n=== 滞后校正设计 (可行) ===\n');
        fprintf('  目标PM=%d°, 实际PM=%.2f°\n', gamma_target, bp.Pm);
        fprintf('  R1=%.0fkΩ, R2=%.0fkΩ, C2=%.1fμF\n', ...
                bp.R1/1e3, bp.R2/1e3, C2_val*1e6);
        fprintf('  Gc(s)=(%.4fs+1)/(%.4fs+1)\n', bp.T, bp.beta*bp.T);
    else
        % 不可行: 给出最优可达PM和所需C2
        bp = best_params;

        % 计算所需最小C2
        % 使用理论设计公式, k=5
        eps_v = 10;
        wc_theory = cotd(gamma_target + eps_v) / 0.3;
        beta_theory = 30 / (wc_theory * sqrt(0.09 * wc_theory^2 + 1));
        T_theory = 5 / wc_theory;
        C2_needed = T_theory / R2_max;

        Gc_best = tf([bp.T, 1], [bp.beta * bp.T, 1]);
        G_comp_best = G_orig * Gc_best;
        G_cl_best = feedback(G_comp_best, 1);
        info_best = stepinfo(G_cl_best);

        result = struct(...
            'feasible', false, ...
            'gamma_target', gamma_target, ...
            'Pm_achieved', bp.Pm, ...
            'Pm_original', Pm0, ...
            'best_R1', bp.R1, 'best_R2', bp.R2, ...
            'T', bp.T, 'beta', bp.beta, 'wc', bp.wc, ...
            'Gc', Gc_best, 'G_comp', G_comp_best, 'G_cl', G_cl_best, ...
            'C2_required', C2_needed, ...
            'overshoot', info_best.Overshoot, ...
            'settling_time', info_best.SettlingTime);

        fprintf('\n=== 滞后校正设计 (不可行!) ===\n');
        fprintf('  目标PM=%d°, 约束下最优PM=%.2f° ✗\n', gamma_target, bp.Pm);
        fprintf('  R1=%.0fkΩ, R2=%.0fkΩ, C2=%.1fμF\n', ...
                bp.R1/1e3, bp.R2/1e3, C2_val*1e6);
        fprintf('  ----------------------------------------\n');
        fprintf('  ★ 要达PM=%d°至少需要 C2≥%.1fμF\n', gamma_target, C2_needed*1e6);
        fprintf('     (或增大R量程至 ≥%.0fkΩ)\n', T_theory/C2_val/1e3);
        fprintf('  原系统 PM=%.2f°, 最优可达 PM=%.2f°\n', Pm0, bp.Pm);
    end
end
