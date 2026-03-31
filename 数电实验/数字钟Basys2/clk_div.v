module clk_div(
    input clk_50m,
    input cr,
    output reg clk_1hz,
    output reg clk_scan
);
    reg [24:0] cnt_1hz;
    reg [15:0] cnt_scan;

    always @(posedge clk_50m or negedge cr) begin
        if (!cr) begin
            cnt_1hz <= 0; clk_1hz <= 0;
            cnt_scan <= 0; clk_scan <= 0;
        end else begin
            // 扫描时钟 (约 380Hz，用于数码管防闪烁)
            cnt_scan <= cnt_scan + 1'b1;
            if (cnt_scan == 16'd65535) clk_scan <= ~clk_scan;

            // 1Hz 计时时钟
            if (cnt_1hz == 25'd24_999_999) begin
                cnt_1hz <= 0;
                clk_1hz <= ~clk_1hz;
            end else begin
                cnt_1hz <= cnt_1hz + 1'b1;
            end
        end
    end
endmodule