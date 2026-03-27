`timescale 1ns / 1ps

module sim;

    reg clk_50m;
    reg cr;
    reg en_clock;
    reg clock_adjust;
    reg clock_alarm_en;
    reg clock_alarm_set;
    reg min_hour_set;
    reg alarm_adjust_disp;

    wire [7:0] pos;
    wire [6:0] seg;
    wire [5:0] segled;
    wire alarm;

    top uut (
        .clk_50m(clk_50m), 
        .cr(cr), 
        .en_clock(en_clock), 
        .clock_adjust(clock_adjust), 
        .clock_alarm_en(clock_alarm_en), 
        .clock_alarm_set(clock_alarm_set), 
        .min_hour_set(min_hour_set), 
        .alarm_adjust_disp(alarm_adjust_disp), 
        .pos(pos), 
        .seg(seg), 
        .segled(segled), 
        .alarm(alarm)
    );

    initial begin
        clk_50m = 0;
        forever #10 clk_50m = ~clk_50m; 
    end

    initial begin
        cr = 0;
        en_clock = 0;
        clock_adjust = 0;
        clock_alarm_en = 0;
        clock_alarm_set = 0;
        min_hour_set = 0;
        alarm_adjust_disp = 0;
        
        #100;
        cr = 1;
        en_clock = 1;
        
        #100000;

        clock_adjust = 1;
        min_hour_set = 1;
        #500000;

        min_hour_set = 0;
        #500000;
        
        clock_adjust = 0;
        
        clock_alarm_set = 1;
        alarm_adjust_disp = 1;
        min_hour_set = 1;
        #300000;
        
        min_hour_set = 0;
        #300000;

        clock_alarm_set = 0;
        alarm_adjust_disp = 0;
        clock_alarm_en = 1;
        
        #2000000;
        
        $stop;
    end

endmodule