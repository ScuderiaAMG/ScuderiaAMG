module c24 (
    input clk,
    input en,
    input cr,
    output [3:0] bcd_u,
    output [3:0] bcd_t
);
    reg [3:0] bcd_ur, bcd_tr;
    assign bcd_u = bcd_ur;
    assign bcd_t = bcd_tr;

    always @(posedge clk or negedge cr) begin
        if (!cr) begin
            bcd_ur <= 0;
            bcd_tr <= 0;
        end else if (en) begin
            if ((bcd_ur == 3) && (bcd_tr == 2)) begin // 24进制计数
                bcd_ur <= 0;
                bcd_tr <= 0;
            end else if (bcd_ur == 9) begin
                bcd_tr <= bcd_tr + 1'b1;
                bcd_ur <= 0;
            end else begin
                bcd_ur <= bcd_ur + 1'b1;
            end
        end
    end
endmodule