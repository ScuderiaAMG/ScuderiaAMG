// ********* counter6.v (BCD: 0~5) **************
module counter6(Q, nCR, EN, CP);
    input CP, nCR, EN;
    output reg [3:0] Q;

    always @(posedge CP or negedge nCR) begin
        if(~nCR) 
            Q <= 4'b0000;          // nCR=0, 异步清零
        else if(~EN) 
            Q <= Q;                // EN=0, 暂停计数
        else if(Q == 4'b0101) 
            Q <= 4'b0000;          // 计满5归零
        else 
            Q <= Q + 1'b1;         // 计数器增1
    end
endmodule