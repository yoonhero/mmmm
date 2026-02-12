FROM --platform=linux/386 i386/alpine:latest

RUN apk update && apk add --no-cache \
    build-base \
    gdb \
    nasm \
    binutils \
    bash \
    vim \
    qemu-i386

WORKDIR /src

RUN echo "set disassembly-flavor att" > /root/.gdbinit

CMD ["/bin/bash"]
