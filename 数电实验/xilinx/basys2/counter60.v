// **** counter60.v (BCD: 00~59) *************
// 60进制计数器: 调用10进制和6进制底层模块构成
module counter60(Cnt, nCR, EN, CP);
    input CP, nCR, EN;
    output [7:0] Cnt;       // 输出为8421 BCD码

    wire ENP;               // 计数器十位的使能信号

    // 计数器的个位 (模10)
    counter10 UC0 (.Q(Cnt[3:0]), .nCR(nCR), .EN(EN), .CP(CP));
    
    // 产生计数器十位的使能信号：个位为9且当前模块被使能时才进位
    assign ENP = EN & (Cnt[3:0] == 4'h9); 
    
    // 计数器的十位 (模6)
    counter6  UC1 (.Q(Cnt[7:4]), .nCR(nCR), .EN(ENP), .CP(CP));
endmodule