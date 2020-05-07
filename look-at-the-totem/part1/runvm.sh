#!/bin/bash

./qemu-system-arm -M versatilepb \
                  -kernel br_arm/output/images/zImage \
                  -dtb br_arm/output/images/versatile-pb.dtb \
                  -append "console=ttyAMA0,115200" -serial stdio \
                  -net nic,model=rtl8139 -net user,hostfwd=tcp::5522-:22 \
                  -monitor telnet:127.0.0.1:55555,server,nowait
