`timescale 1ns / 1ps

module test;

    // Inputs
    reg clk_100m;
    reg cr;

    // Outputs
    wire clk_1k;
    wire clk_5h;
    wire clk_1hz;

    parameter PERIOD = 10;

    // 实例化被测单元 (UUT)
    clk_div uut (
        .clk_100m(clk_100m),
        .clk_1k(clk_1k),
        .clk_5h(clk_5h),
        .clk_1hz(clk_1hz),
        .cr(cr)
    );

    // 产生 100MHz 系统时钟 (驱动 clk_100m 而不是 clk)
    always begin
        clk_100m = 1'b0;
        #(PERIOD/2) clk_100m = 1'b1;
        #(PERIOD/2);
    end

    initial begin
        // 初始化输入
        clk_100m = 0;
        cr = 0;  // 初始给低电平，让系统复位清零
        
        // 等待 100ns 后撤销复位
        #100;
        cr = 1;  // 复位拉高，分频器开始正常计数工作
        
        // 让仿真跑一段时间观察波形
        // 注意：如果要看到 1Hz 翻转，仿真时间需要设得非常长，
        // 建议你把 clk_div 里面的计数值改小一点来进行仿真测试。
        #100000; 
    end

endmodule