This is unfold of https://github.com/geohot/fromthetransistor.

**FPGA is a bunch of Transistors**

- `common circuit` and `common emitter amplifier circuit`
    - `npn` vs `pnp`: why `npn` is better in many case over `pnp`.
- build ALU, 256B RAM with only `nand` ([digital logic sim](https://sebastian.itch.io/digital-logic-sim))
- how FPGA(LUT+FF) works - [reverse-engineering first fpga chip](https://semiwiki.com/fpga/290990-reverse-engineering-the-first-fpga-chip-xilinx-xc2064/)
    - CPU is neighbor - ["Hello, world" from scratch on a 6502](https://www.youtube.com/watch?v=LnzuMJLZRdU)
    - NMOS, PMOS and ALU! - [8008 ALU](https://www.righto.com/2017/02/reverse-engineering-surprisingly.html)

**Hardward oriented lang, Verilog**

- learn verilog (iverilog+gtkwave+...verilator?) :>
    - [old](https://vol.verilog.com/VOL/main.htm)
    - [modern](https://zipcpu.com/tutorial/)
    - [in one day](https://asic-world.com/verilog/verilog_one_day.html)
- build LED blinking + UART
