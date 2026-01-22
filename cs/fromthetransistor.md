This is unfold++ of https://github.com/geohot/fromthetransistor.

**FPGA is a bunch of Transistors**

-   `common circuit` and `common emitter amplifier circuit`
    -   `npn` vs `pnp`: why `npn` is better in many case over `pnp`.
-   build ALU, 256B RAM with only `nand` ([digital logic sim](https://sebastian.itch.io/digital-logic-sim))
-   how FPGA(LUT+FF) works - [reverse-engineering first fpga chip](https://semiwiki.com/fpga/290990-reverse-engineering-the-first-fpga-chip-xilinx-xc2064/)
    -   CPU is neighbor - ["Hello, world" from scratch on a 6502](https://www.youtube.com/watch?v=LnzuMJLZRdU)
    -   NMOS, PMOS and ALU! - [8008 ALU](https://www.righto.com/2017/02/reverse-engineering-surprisingly.html)

**Hardware oriented lang, Verilog**

-   learn verilog with iverilog+gtkwave
    -   if you are looking for learning materials? -> [old](https://vol.verilog.com/VOL/main.htm)/[modern](https://zipcpu.com/tutorial/)/[in one day](https://asic-world.com/verilog/verilog_one_day.html)
-   build LED blinking("Hello World" in HW)
-   build UART (MMIO, QEMU)

**Midterm proj - Have a fun with [Brainfuck](https://esolangs.org/wiki/Brainfuck)**

-   [BF Chip in DLS](./bf_sheet.md) - much simpler than ARM's but BF is actually turing complete! So you "can" build anything.
    -   BF Assembler - BF->BF Chip ISA(I defined)
    -   It's [Snake Game](./bf/bf-is-turing-complete.py)

**Make practical one, Arm7**

> Say bye, bye to mos6502 and bf chip...
