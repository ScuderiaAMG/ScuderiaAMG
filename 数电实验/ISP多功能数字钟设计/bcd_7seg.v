module bcd_7seg(
    input [3:0] bcd,
    output [6:0] seg
    );
reg [6:0] seg1;
assign seg =seg1;
always @(bcd)
case (bcd)
        4'b0000  : seg1 <= 7'b1000000;//40
        4'b0001  : seg1 <= 7'b1111001;//79
        4'b0010  : seg1 <= 7'b0100100;//24
        4'b0011  : seg1 <= 7'b0110000;//30
        4'b0100  : seg1 <= 7'b0011001;//19
        4'b0101  : seg1 <= 7'b0010010;//12
        4'b0110  : seg1 <= 7'b0000010;//2
        4'b0111  : seg1 <= 7'b1111000;//78
        4'b1000  : seg1 <= 7'b0000000;//0
        4'b1001  : seg1 <= 7'b0010000; //10
        default  : seg1 <= 7'b1111111;
endcase
endmodule