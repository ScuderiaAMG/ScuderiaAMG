module c60 (
    input clk,
    input en,
    input cr,
    output rco,
    output [3:0] bcd_t,
    output [3:0] bcd_u
);
    wire rco_u, rco_t;
    assign rco = rco_u & rco_t;

    c10 units (.clk(clk), .en(en), .cr(cr), .rco(rco_u), .bcd10(bcd_u));
    c6  tens  (.clk(clk), .en(rco_u & en), .cr(cr), .rco(rco_t), .bcd6(bcd_t));
endmodule