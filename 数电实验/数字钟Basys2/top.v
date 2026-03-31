module top(
    input clk_50m,
    input cr,             // SW0 (低电平复位)
    input adjust,         // SW1 (1:校时模式, 0:正常运行)
    input min_hour_set,   // SW2 (0:调分, 1:调时)
    input btn_add,        // BTN0 (增加键)
    output [7:0] led,     // LD7~LD0 (显示秒钟BCD)
    output [3:0] an,      // AN3~AN0
    output [6:0] seg      // CA~CG
);
    wire clk_1hz, clk_scan;
    wire [3:0] bcd_su, bcd_st, bcd_mu, bcd_mt, bcd_hu, bcd_ht;
    
    // 按键边沿检测 (用于单步调节时间)
    reg btn_d1, btn_d2;
    always @(posedge clk_scan) begin
        btn_d1 <= btn_add;
        btn_d2 <= btn_d1;
    end
    wire btn_pulse = btn_d1 & ~btn_d2;

    // 模块例化
    clk_div u_clk_div (
        .clk_50m(clk_50m), .cr(cr), 
        .clk_1hz(clk_1hz), .clk_scan(clk_scan)
    );

    clock_adjust u_clk_adj (
        .clk_1hz(clk_1hz), .adjust(adjust), .cr(cr), 
        .min_hour_set(min_hour_set), .btn_pulse(btn_pulse),
        .bcd_su(bcd_su), .bcd_st(bcd_st),
        .bcd_mu(bcd_mu), .bcd_mt(bcd_mt),
        .bcd_hu(bcd_hu), .bcd_ht(bcd_ht)
    );

    scan_disp u_scan_disp (
        .clk_scan(clk_scan),
        .bcd_hu(bcd_hu), .bcd_ht(bcd_ht),
        .bcd_mu(bcd_mu), .bcd_mt(bcd_mt),
        .seg(seg), .an(an)
    );

    // 将秒输出到LED
    assign led = {bcd_st, bcd_su};

endmodule