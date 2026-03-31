module clock_adjust(
    input clk_1hz,
    input adjust,        // 校时模式使能
    input cr,
    input min_hour_set,  // 0:调分, 1:调时
    input btn_pulse,     // 手动调整脉冲
    output [3:0] bcd_su, bcd_st,
    output [3:0] bcd_mu, bcd_mt,
    output [3:0] bcd_hu, bcd_ht
);
    wire m_en, h_en, rco_s, rco_m;
    
    // 正常计时使能 vs 校时手动脉冲使能
    wire normal_run = ~adjust;
    assign m_en = (normal_run & rco_s) | (adjust & ~min_hour_set & btn_pulse);
    assign h_en = (normal_run & rco_s & rco_m) | (adjust & min_hour_set & btn_pulse);

    c60 second (.clk(clk_1hz), .en(normal_run), .cr(cr), .rco(rco_s), .bcd_t(bcd_st), .bcd_u(bcd_su));
    c60 minute (.clk(clk_1hz), .en(m_en), .cr(cr), .rco(rco_m), .bcd_t(bcd_mt), .bcd_u(bcd_mu));
    c24 hour   (.clk(clk_1hz), .en(h_en), .cr(cr), .bcd_u(bcd_hu), .bcd_t(bcd_ht));
endmodule