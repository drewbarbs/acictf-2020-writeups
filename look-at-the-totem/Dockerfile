FROM ubuntu:18.04

# Install dependencies for using buildroot, fetch some QEMU firmware
# bins we'll use to run the qemu-system emulators.
RUN apt update && apt install -y qemu gdb build-essential \
        git libglib2.0-dev libfdt-dev libpixman-1-dev zlib1g-dev \
        openssh-client wget flex bison libncurses5-dev patch gzip \
        bzip2 perl tar cpio unzip rsync bc python3 python nasm telnet \
        netcat

WORKDIR /src
RUN wget https://buildroot.org/downloads/buildroot-2020.02.1.tar.bz2
RUN git clone https://git.qemu.org/git/qemu.git && cd qemu && git checkout v2.11.0 && git submodule update --init

WORKDIR /src/qemu
COPY common/fix_memfd.patch .
RUN patch -p1 <fix_memfd.patch

# Make debug builds of QEMU to compare with challenge binaries
RUN mkdir -p /src/part1/qemu-debug-build && \
        cd /src/part1/qemu-debug-build && \
        /src/qemu/configure --target-list=arm-softmmu \
                            --enable-debug \
                            --disable-werror \
                            --enable-capstone=git && \
        make -j$(nproc)

# Make debug builds of QEMU to compare with challenge binaries
RUN mkdir -p /src/part2/qemu-debug-build && \
        cd /src/part2/qemu-debug-build && \
        /src/qemu/configure --target-list=x86_64-softmmu \
                            --enable-debug \
                            --disable-werror \
                            --enable-capstone=git && \
        make -j$(nproc)

COPY common/chalbins.tgz /src/

RUN mkdir -p /src/part1/br_arm && \
        tar xf /src/buildroot-2020.02.1.tar.bz2 -C /src/part1/br_arm --strip-components 1
WORKDIR /src/part1/br_arm
COPY part1/br2_arm.config configs/my_defconfig
# this takes forever (buildroot scales the build to available # of cpus, don't use "-j" flag)
RUN make my_defconfig && make

WORKDIR /src/part1
RUN tar xf /src/chalbins.tgz qemu-system-arm tpmutil
# Copy some runtime dependencies from our system QEMU
RUN cp /usr/share/qemu/keymaps/en-us /usr/lib/ipxe/qemu/efi-rtl8139.rom .
RUN ssh-keygen -t rsa -q -N '' -f id_rsa
# Update the image with our public key
RUN mkdir -p br_arm/output/target/root/.ssh && chmod 600 br_arm/output/target/root/.ssh
RUN cp id_rsa.pub br_arm/output/target/root/.ssh/authorized_keys && cd br_arm && make

RUN mkdir -p /src/part2/br_x86_64 && \
        tar xf /src/buildroot-2020.02.1.tar.bz2 -C /src/part2/br_x86_64 --strip-components 1
WORKDIR /src/part2/br_x86_64
COPY part2/br2_x86_64.config configs/my_defconfig
RUN make my_defconfig && make

WORKDIR /src/part2
RUN tar xf /src/chalbins.tgz qemu-system-x86_64
# Copy some runtime dependencies from our system QEMU
RUN cp /usr/share/qemu/keymaps/en-us /usr/lib/ipxe/qemu/efi-rtl8139.rom .
RUN ssh-keygen -t rsa -q -N '' -f id_rsa
# Update the image with our public key
RUN mkdir -p br_x86_64/output/target/root/.ssh && chmod 600 br_x86_64/output/target/root/.ssh
RUN cp id_rsa.pub br_x86_64/output/target/root/.ssh/authorized_keys && cd br_x86_64 && make

WORKDIR /src
COPY part1/Makefile part1/exploit.c common/reverse_shell.nasm part1/runvm.sh part1/runexploit.sh part1/

COPY part2/Makefile part2/exploit.c common/reverse_shell.nasm part2/runvm.sh part2/runexploit.sh part2/
