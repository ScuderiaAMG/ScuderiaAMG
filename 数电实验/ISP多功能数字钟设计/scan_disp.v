module scan_disp(
    input clk,
    input cr,
    input en,
    input [3:0] ch0,
    input [3:0] ch1,
    input [3:0] ch2,
    input [3:0] ch3,
    input [3:0] ch4,
    input [3:0] ch5,
    output [6:0] seg,
    output [7:0] pos
    );
wire rco;
wire [3:0] bcdsel,bcd_data;
c6 u_count(clk,cr,rco,en,bcdsel);//6进制同步计数器
mux6_1 u_mux(ch0,ch1,ch2,ch3,ch4,ch5,bcdsel,bcd_data);//6路4位复用器
posdecode u_pos(bcdsel,pos);//位码
bcd_7seg u_seg(bcd_data,seg);//段码
endmodule