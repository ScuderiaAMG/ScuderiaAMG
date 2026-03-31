module c10 (
    input clk,
    input en,
    input cr,
    output rco,
    output [3:0] bcd10
);
    reg [3:0] bcd10r;
    assign rco = (bcd10r == 9) ? 1'b1 : 1'b0; // 进位信号
    assign bcd10 = bcd10r;

    always @(posedge clk or negedge cr) begin
        if (!cr)
            bcd10r <= 0;
        else if (en) begin
            if (bcd10r < 9)
                bcd10r <= bcd10r + 1'b1;
            else
                bcd10r <= 0;
        end
    end
endmodule