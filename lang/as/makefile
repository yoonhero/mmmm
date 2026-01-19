hello: hello.o
	ld -o hello hello.o -lSystem -syslibroot `xcrun -sdk macosx --show-sdk-path` -e _start -arch arm64

hello.o: hello.s
	as -arch arm64 -o hello.o hello.s

# in fact just call `clang hello.s -o hello` xkcd :>
run:
	make hello.o
	make hello
	./hello