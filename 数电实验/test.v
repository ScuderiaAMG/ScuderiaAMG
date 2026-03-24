`timescale 1ns / 1ps

////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer:
//
// Create Date:   20:49:57 03/10/2026
// Design Name:   full_adder
// Module Name:   C:/check/full_adder/test.v
// Project Name:  full_adder
// Target Device:  
// Tool versions:  
// Description: 
//
// Verilog Test Fixture created by ISE for module: full_adder
//
// Dependencies:
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
////////////////////////////////////////////////////////////////////////////////

module test;

	// Inputs
	reg A;
	reg B;
	reg Cin;

	// Outputs
	wire Sum;
	wire Cout;

	// Instantiate the Unit Under Test (UUT)
	full_adder uut (
		.A(A), 
		.B(B), 
		.Cin(Cin), 
		.Sum(Sum), 
		.Cout(Cout)
	);

	initial begin
		// Initialize Inputs
		A = 0;
		B = 0;
		Cin = 0;

		// Wait 100 ns for global reset to finish
		#100 A = 0; B = 0; Cin = 1;
		#100 A = 0; B = 1; Cin = 0;
		#100 A = 0; B = 1; Cin = 1;
		#100 A = 1; B = 0; Cin = 0;
		#100 A = 1; B = 0; Cin = 1;
		#100 A = 1; B = 1; Cin = 0;
		#100 A = 1; B = 1; Cin = 1;
        
		// Add stimulus here

	end
      
endmodule

