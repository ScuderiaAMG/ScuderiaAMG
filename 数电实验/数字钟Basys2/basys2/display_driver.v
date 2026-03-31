// **** display_driver.v (数码管动态扫描) *************
module display_driver(
    input clk_1khz,        // 1kHz 扫描时钟
    input [7:0] Hr,        // 小时 BCD 码
    input [7:0] Min,       // 分钟 BCD 码
    output reg [3:0] AN,   // 4位位选 (低电平有效)
    output reg [7:0] SEG   // 8段段选 (低电平有效，SEG[7]为小数点)
);

    reg [1:0] scan_cnt;    // 2位计数器，用于切换4个数码管
    reg [3:0] current_bcd; // 当前正在显示的 BCD 数字

    // 扫描计数器
    always @(posedge clk_1khz) begin
        scan_cnt <= scan_cnt + 1'b1;
    end

    // 位选信号产生与数据多路选择
    always @(*) begin
        case(scan_cnt)
            2'b00: begin AN = 4'b1110; current_bcd = Min[3:0]; end // 最右侧数码管：分个位
            2'b01: begin AN = 4'b1101; current_bcd = Min[7:4]; end // 右二数码管：分十位
            2'b10: begin AN = 4'b1011; current_bcd = Hr[3:0];  end // 左二数码管：时个位
            2'b11: begin AN = 4'b0111; current_bcd = Hr[7:4];  end // 最左侧数码管：时十位
            default: begin AN = 4'b1111; current_bcd = 4'h0; end
        endcase
    end

    // 七段译码器 (共阳极/低电平点亮，Basys2开发板适用)
    // 对应关系: {DP, CG, CF, CE, CD, CC, CB, CA}
    always @(*) begin
        case(current_bcd)
            4'h0: SEG = 8'b1100_0000;
            4'h1: SEG = 8'b1111_1001;
            4'h2: SEG = 8'b1010_0100;
            4'h3: SEG = 8'b1011_0000;
            4'h4: SEG = 8'b1001_1001;
            4'h5: SEG = 8'b1001_0010;
            4'h6: SEG = 8'b1000_0010;
            4'h7: SEG = 8'b1111_1000;
            4'h8: SEG = 8'b1000_0000;
            4'h9: SEG = 8'b1001_0000;
            default: SEG = 8'b1111_1111; // 熄灭
        endcase
        
        // 可选：在小时和分钟之间点亮小数点作为分隔符
        if (scan_cnt == 2'b10) 
            SEG[7] = 1'b0; // 点亮时个位的小数点
    end

endmodule