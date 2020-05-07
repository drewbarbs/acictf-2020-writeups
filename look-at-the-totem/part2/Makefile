CC=$(PWD)/br_x86_64/output/host/bin/x86_64-buildroot-linux-uclibc-gcc
LD=$(PWD)/br_x86_64/output/host/bin/x86_64-buildroot-linux-uclibc-ld

exploit: exploit.c shellcode.o
	$(CC) -o $@ $^

shellcode.o: shellcode.bin
	$(LD) -r -b binary -o $@ $^

shellcode.bin: reverse_shell.nasm
	nasm -f bin -o $@ $^
