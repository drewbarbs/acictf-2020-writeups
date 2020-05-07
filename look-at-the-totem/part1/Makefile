CC=$(PWD)/br_arm/output/host/bin/arm-buildroot-linux-uclibcgnueabi-gcc
LD=$(PWD)/br_arm/output/host/bin/arm-buildroot-linux-uclibcgnueabi-ld

exploit: exploit.c shellcode.o
	$(CC) -o $@ $^

shellcode.o: shellcode.bin
	$(LD) -r -b binary -o $@ $^

shellcode.bin: reverse_shell.nasm
	nasm -f bin -o $@ $^
