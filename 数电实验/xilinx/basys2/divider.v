// **** divider.v (50MHz -> 1Hz) *************
module divider(
    input clk_50m, 
    input nCR, 
    output reg clk_1hz
);
    reg [24:0] count; // 至少需要25位来存储 25,000,000 的计数值

    always @(posedge clk_50m or negedge nCR) begin
        if (~nCR) begin
            count <= 0;
            clk_1hz <= 0;
        end else if (count == 25000000 - 1) begin
            count <= 0;
            clk_1hz <= ~clk_1hz;  // 计数达到一半时翻转，得到1Hz
        end else begin
            count <= count + 1;
        end
    end
endmodule