module second_LED(
    input clk,
    input cr,
    input en,
    input [3:0] st,
    input [3:0] su,
    output [5:0] segled
);

reg [5:0] second;
wire [7:0] sed;
assign segled=second;
assign sed={st[3:0],su[3:0]};

always @ (sed)
    case (sed)
        8'b00000000:second<=6'b000000;
        8'b00000001:second<=6'b000001;
        8'b00000010:second<=6'b000010;
        8'b00000011:second<=6'b000011;
        8'b00000100:second<=6'b000100;
        8'b00000101:second<=6'b000101;
        8'b00000110:second<=6'b000110;
        8'b00000111:second<=6'b000111;
        8'b00001000:second<=6'b001000;
        8'b00001001:second<=6'b001001;
        8'b00010000:second<=6'b001010;
        8'b00010001:second<=6'b001011;
        8'b00010010:second<=6'b001100;
        8'b00010011:second<=6'b001101;
        8'b00010100:second<=6'b001110;
        8'b00010101:second<=6'b001111;
        8'b00010110:second<=6'b010000;
        8'b00010111:second<=6'b010001;
        8'b00011000:second<=6'b010010;
        8'b00011001:second<=6'b010011;
        8'b00100000:second<=6'b010100;
        8'b00100001:second<=6'b010101;
        8'b00100010:second<=6'b010110;
        8'b00100011:second<=6'b010111;
        8'b00100100:second<=6'b011000;
        8'b00100101:second<=6'b011001;
        8'b00100110:second<=6'b011010;
        8'b00100111:second<=6'b011011;
        8'b00101000:second<=6'b011100;
        8'b00101001:second<=6'b011101;
        8'b00110000:second<=6'b011110;
        8'b00110001:second<=6'b011111;
        8'b00110010:second<=6'b100000;
        8'b00110011:second<=6'b100001;
        8'b00110100:second<=6'b100010;
        8'b00110101:second<=6'b100011;
        8'b00110110:second<=6'b100100;
        8'b00110111:second<=6'b100101;
        8'b00111000:second<=6'b100110;
        8'b00111001:second<=6'b100111;
        8'b01000000:second<=6'b101000;
        8'b01000001:second<=6'b101001;
        8'b01000010:second<=6'b101010;
        8'b01000011:second<=6'b101011;
        8'b01000100:second<=6'b101100;
        8'b01000101:second<=6'b101101;
        8'b01000110:second<=6'b101110;
        8'b01000111:second<=6'b101111;
        8'b01001000:second<=6'b110000;
        8'b01001001:second<=6'b110001;
        8'b01010000:second<=6'b110010;
        8'b01010001:second<=6'b110011;
        8'b01010010:second<=6'b110100;
        8'b01010011:second<=6'b110101;
        8'b01010100:second<=6'b110110;
        8'b01010101:second<=6'b110111;
        8'b01010110:second<=6'b111000;
        8'b01010111:second<=6'b111001;
        8'b01011000:second<=6'b111010;
        8'b01011001:second<=6'b111011;
        default:second<=6'b111111;
    endcase

endmodule