module scan_disp(
    input clk_scan,
    input [3:0] bcd_hu, bcd_ht,
    input [3:0] bcd_mu, bcd_mt,
    output reg [6:0] seg,
    output reg [3:0] an
);
    reg [1:0] scan_cnt;
    reg [3:0] bcd_data;
    wire [6:0] seg_data;

    bcd_7seg u_seg (.bcd(bcd_data), .seg(seg_data));

    always @(posedge clk_scan) begin
        scan_cnt <= scan_cnt + 1'b1;
        case (scan_cnt)
            2'b00: begin an <= 4'b1110; bcd_data <= bcd_mu; end // 分个位
            2'b01: begin an <= 4'b1101; bcd_data <= bcd_mt; end // 分十位
            2'b10: begin an <= 4'b1011; bcd_data <= bcd_hu; end // 时个位
            2'b11: begin an <= 4'b0111; bcd_data <= bcd_ht; end // 时十位
        endcase
        seg <= seg_data;
    end
endmodule