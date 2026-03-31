// **** top_clock.v (修改后的顶层模块) *************
module top_clock(
    input clk_50m,      // 50MHz系统时钟
    input nCR,          // 异步复位键 (低电平有效，对应SW0)
    input AdjMinKey,    // 调分按键 (高电平有效，对应BTN0)
    input AdjHrKey,     // 调时按键 (高电平有效，对应BTN1)
    
    output [7:0] Sec,   // 秒显示 (输出到LED)
    output [3:0] AN,    // 数码管位选
    output [7:0] SEG    // 数码管段选
);

    wire clk_1hz;
    reg clk_1khz;
    reg [15:0] cnt_1k;
    
    wire [7:0] Hr_internal;  // 内部连接的小时BCD码
    wire [7:0] Min_internal; // 内部连接的分钟BCD码
    
    wire min_carry, hr_carry;
    wire min_en, hr_en;

    // 1. 产生 1Hz 走时钟 (之前写的divider模块)
    divider U_Div (
        .clk_50m(clk_50m),
        .nCR(nCR),
        .clk_1hz(clk_1hz)
    );

    // 2. 产生 1kHz 扫描时钟 (50MHz / 50000 = 1kHz)
    always @(posedge clk_50m or negedge nCR) begin
        if (~nCR) begin
            cnt_1k <= 0;
            clk_1khz <= 0;
        end else if (cnt_1k >= 16'd24999) begin
            cnt_1k <= 0;
            clk_1khz <= ~clk_1khz;
        end else begin
            cnt_1k <= cnt_1k + 1'b1;
        end
    end

    // 3. 秒计数器
    counter60 U_Sec (
        .Cnt(Sec), 
        .nCR(nCR), 
        .EN(1'b1), 
        .CP(clk_1hz)
    );

    // 进位与校时控制逻辑：
    assign min_carry = (Sec == 8'h59);
    assign min_en = min_carry | AdjMinKey; 

    // 4. 分钟计数器
    counter60 U_Min (
        .Cnt(Min_internal), 
        .nCR(nCR), 
        .EN(min_en), 
        .CP(clk_1hz)
    );

    // 进位与校时控制逻辑：
    assign hr_carry = (Min_internal == 8'h59) && min_carry;
    assign hr_en = hr_carry | AdjHrKey;

    // 5. 小时计数器
    counter24 U_Hr (
        .Cnt(Hr_internal), 
        .nCR(nCR), 
        .EN(hr_en), 
        .CP(clk_1hz)
    );
    
    // 6. 实例化数码管显示驱动
    display_driver U_Display (
        .clk_1khz(clk_1khz),
        .Hr(Hr_internal),
        .Min(Min_internal),
        .AN(AN),
        .SEG(SEG)
    );

endmodule