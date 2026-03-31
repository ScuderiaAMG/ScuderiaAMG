`timescale 1ns / 1ps
module top_tb;
    reg clk_50m;
    reg cr;
    reg adjust;
    reg min_hour_set;
    reg btn_add;

    wire [7:0] led;
    wire [3:0] an;
    wire [6:0] seg;

    top uut (
        .clk_50m(clk_50m), .cr(cr), .adjust(adjust), 
        .min_hour_set(min_hour_set), .btn_add(btn_add), 
        .led(led), .an(an), .seg(seg)
    );

    // 产生 50MHz 时钟 (20ns 周期)
    always #10 clk_50m = ~clk_50m;

    initial begin
        clk_50m = 0;
        cr = 0;
        adjust = 0;
        min_hour_set = 0;
        btn_add = 0;

        // 全局复位
        #100;
        cr = 1;

        // 进入校时模式：调分钟
        #500;
        adjust = 1;
        min_hour_set = 0; 
        
        // 模拟按下调整键
        #100 btn_add = 1;
        #100 btn_add = 0;

        // 恢复正常运行
        #500;
        adjust = 0;
    end
endmodule