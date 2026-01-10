// Verilog allows us to design a Digital design at Behavior Level, Register
// Transfer Level, Gate Level and switch level.

// run with iverilog + gtkwave(not essential)
//   iverilog -o led.vvp -s tb LED.v
//   vvp led.vvp

// Verilog model = union of modules
//
// module <name> (<ports: [input, output, inout]>);
//    /* signal */
//    // declare wire, reg, parameter
//    
//    // assign(wire), always(reg), initial, submodule instance...
// endmodule
//

`timescale 1ms / 1ps

module led (a, led);
  input a;
  output led;
  assign led = a;
endmodule

module t_ff (
  input wire clk,
  input wire rst_n, //(reset pin is necessary)
  input wire T,
  output reg Q
);
  always @(posedge clk or negedge rst_n) begin // level sensitive(combinational circuits) vs. edge sensitive(FF)
    if (!rst_n) Q <= 1'b0;
    else if (T) Q <= ~Q; // not cover all cases + trying to combinational statement -> Latch!
    //else   Q <= Q; // in short, Q^T
    // procedural logic (<=) vs. combination logic (=)
  end
endmodule

module counter (
  input wire clk,
  input wire rst_n,
  output wire [1:0] q
);
  parameter T = 1'b1;
  wire q_clk1, q_clk2;
  wire clk2;

  assign clk2 = ~q_clk1;

  t_ff d1 (
    .clk (clk),
    .rst_n (rst_n),
    .T   (T),
    .Q   (q_clk1)
  );
  t_ff d2 (
    .clk (clk2),
    .rst_n (rst_n),
    .T   (T),
    .Q   (q_clk2)
  );

  assign q = {q_clk2, q_clk1}; // {}: concat & {{}}: multiply -> {3{2'b01}}=6'b010101
endmodule

module tb;
  reg clk, rst_n;
  reg a;
  wire led; // 0, 1, z(high impedence), x(unknown)
  wire [1:0] cnt;

  parameter delay = 5; // 100Hz - compile time
  parameter state = 2'b11; // <width>'<base><value>

  led dut_led (.a(a), .led(led));
  counter dut_counter (.clk(clk), .rst_n(rst_n), .q(cnt));

  always #delay clk = ~clk;

  always @(posedge clk) begin
    //if (!cnt) a = ~a;
    a = ~a;
    if (cnt == state) $finish;
  end
  
  initial begin
    // $dumpfile("led.vcd");
    // $dumpvars(0, root);
    $monitor("clk=%d a=%b led=%b cnt=%d", clk, a, led, cnt);
    clk = 0;
    a = 0;
    rst_n = 1'b0;
    #delay rst_n = 1'b1;
  end
endmodule
