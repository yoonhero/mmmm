echo "compile it"
iverilog -o $1.vvp -s tb $1.v
echo "Run $1.vvp file"
vvp $1.vvp
