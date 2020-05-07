#!/bin/bash

./qemu-system-x86_64 -L /usr/share/seabios \
	-kernel br_x86_64/output/images/bzImage \
	-serial none \
	-monitor telnet:127.0.0.1:55555,server,nowait \
	-display none \
	-net nic,model=rtl8139 -net nic,model=rtl8139 \
	-net user,hostfwd=tcp::6622-:22 \
	-no-reboot \
	-device pwn
