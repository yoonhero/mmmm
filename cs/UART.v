// Universal asynchronous receiver-transmitter
//
// signal levels
//   RS-232 : single-ended signal (~= Raw TTL)
//   RS-485 : differntial signal
//
// baud rate(not like bps) / parity bit / flow control?
//   

// `timescale 1us/100ns // 100Mhz ~ 115200 baudrate

module uart(
  input reset,

  input rxclk,
  input rx_in,
  output reg [7:0] rx_data,
  output reg rx_empty,
  output reg rx_error,

  input txclk,
  output reg tx_out,
  input [7:0] tx_data,
  output reg tx_empty
);
  reg clk; // clock generator

  reg rx_idle;
  reg [7:0] rx_reg;
  reg [3:0] rx_cnt;
  reg rx_d1, rx_d2;

  reg [3:0] tx_cnt;

  // 8N1(no parity and 1 stop bit) = 8/10 efficiency
  // -> Ethernet's protocol efficiency (maximum throughput frames) = 95%(1500B)
  //    99%(9000B)
  always @(posedge rxclk or posedge reset) begin
    if (reset) begin
      rx_data <= 0;
      rx_reg <= 0;
      rx_idle <= 1;
      rx_empty <= 1;
    end else begin
      rx_d1 <= rx_in;
      rx_d2 <= rx_d1;

      if (rx_idle && rx_d2 == 0) begin // start bit(0)
        rx_cnt <= 1;
        rx_idle <= 0;
        rx_empty <= 1;
      end

      if (rx_idle == 0) begin
        rx_cnt <= rx_cnt + 1;
        if (rx_cnt == 0) begin
          rx_error <= 1;
        end
        if (rx_cnt > 0 && rx_cnt < 9) begin
          rx_reg[rx_cnt - 1] <= rx_d2;
        end
        if (rx_cnt == 9) begin
          rx_data <= rx_reg;
          rx_idle <= 1;

          if (rx_d2 != 1) begin
            rx_error <= 1; // it must end with 1(stop sign)
          end else begin
            rx_error <= 0;
            rx_empty <= 0;
          end
        end 
      end
    end
  end

  always @(negedge txclk or posedge reset) begin
    if (reset) begin
      tx_out <= 1;
      tx_cnt <= 0;
      tx_empty <= 1;
    end else begin
      if (!tx_empty) begin
        tx_cnt <= tx_cnt + 1;
        if (tx_cnt == 0) begin // start bit(0) 
          tx_out <= 0;
        end
        if (tx_cnt > 0 && tx_cnt < 9) begin
          tx_out <= tx_data[tx_cnt - 1];
        end
        if (tx_cnt == 9) begin // stop sign(1)
          tx_out <= 1; // it keeps idle status.
          tx_cnt <= 0;
          tx_empty <= 1;
        end
     end
    end
  end
endmodule

module tb();
  reg reset;
  reg clk;
  reg sig;
  wire [7:0] data;
  wire done;
  wire rx_empty, rx_error;
  assign done = ~rx_empty;

  parameter tick = 10;

  parameter send = 8'b11001110;
  reg [3:0] cnt;
  
  uart UART (.reset(reset), .rxclk(clk), .rx_in(sig), .rx_data(data), .rx_empty(rx_empty), .rx_error(rx_error));

  always #tick clk = ~clk;

  initial begin
    $monitor("At time %0t: sig=%b, cnt=%d, done=%b, error=%b", $time, sig, cnt, done, rx_error);
    clk = 0;
    sig = 1;
    cnt = 0;
    reset = 1;
    #tick reset = 0;
  end

  always @(posedge clk) begin
    if (done || rx_error) begin
      $display("data sent: %b, received: %b", send, data);
      $finish;
    end else begin
      cnt <= cnt + 1;
      if (cnt == 0) begin
        sig <= 0;
      end
      if (cnt > 0 && cnt < 9) begin
        sig <= send[cnt - 1];
      end
      if (cnt == 9) begin
        sig <= 1;
      end
    end
  end
endmodule
