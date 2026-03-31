// **** counter24.v (BCD: 00~23) *************
module counter24(Cnt, nCR, EN, CP);
    input CP, nCR, EN;
    output reg [7:0] Cnt;

    always @(posedge CP or negedge nCR) begin
        if (~nCR) begin
            Cnt <= 8'h00;
        end else if (EN) begin
            if (Cnt == 8'h23) begin
                Cnt <= 8'h00;            // 计满23清零
            end else if (Cnt[3:0] == 4'h9) begin
                Cnt[3:0] <= 4'h0;        // 个位满9，向十位进位
                Cnt[7:4] <= Cnt[7:4] + 1'b1;
            end else begin
                Cnt[3:0] <= Cnt[3:0] + 1'b1; // 个位正常加1
            end
        end
    end
endmodule