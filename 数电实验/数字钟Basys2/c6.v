module c6 (
    input clk,
    input cr,
    input en,
    output rco,
    output [3:0] bcd6
);
    reg [3:0] bcd6r;
    assign rco = (bcd6r == 5) ? 1'b1 : 1'b0; // 进位信号
    assign bcd6 = bcd6r;

    always @(posedge clk or negedge cr) begin
        if (!cr)
            bcd6r <= 4'b0000;
        else if (en) begin
            if (bcd6r != 5)
                bcd6r <= bcd6r + 1'b1;
            else
                bcd6r <= 0;
        end
    end
endmodule