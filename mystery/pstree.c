#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <stdint.h>
#include <errno.h>

// POSIX - standards describing the OS interface for C.
typedef struct {
    uint32_t pid;
    uint32_t nchild;
    uint32_t payload_bytes;
} __attribute__((packed)) MsgHdr;

// IPC - share mem + (pipes + mq(tt) + socket):message passing
// ---> using poll/select pattern...
size_t nchild = 0;
int c2p_pipes[8][2]; // [child][read/write]
int to_parent[2];

static int readn(int fd, void *p, size_t n) {
    uint8_t *cur = (uint8_t*)p;
    size_t got = 0;
    while (got < n) {
        ssize_t r = read(fd, cur+got, n-got);
        if (r < 0) {if (errno == EINTR) continue; return -1;} 
        if (r == 0) return 0;
        got += (size_t)r;
    }
    return 1;
}

static int written(int fd, const void *p, size_t n) {
    const uint8_t *cur = (const uint8_t *)p;
    size_t sent = 0;
    while (sent < n) {
        ssize_t r = write(fd, cur+sent, n-sent);
        if (r < 0) {if(errno == EINTR) continue; return -1;}
        sent += (size_t)r;
    }
    return 1;
}

static int recv_blob(int fd, uint8_t **out, uint32_t *out_len) {
    uint32_t len;
    if (readn(fd, &len, sizeof len) <= 0) return 0;
    uint8_t *buf = (uint8_t*)malloc(len);
    if (!buf) return -1;
    if (readn(fd, buf, len) <= 0) {free(buf); return 0;}
    *out = buf; *out_len = len;
    return 1;
} 
static int send_blob(int fd, const uint8_t *buf, uint32_t len) {
    if (written(fd, &len, sizeof len) < 0) return -1;
    if (len && written(fd, buf, len) < 0) return -1;
    return 1;
} 

// fork+execve(Unix) = Create Process(window)
static int createProcess();

typedef struct PNode {
    uint32_t pid;
    uint32_t nchild;
    struct PNode *childs;
} PNode;

static PNode deserialize(uint8_t *blob) {
    uint8_t *p = blob;
    MsgHdr hdr;
    memcpy(&hdr, blob, sizeof(hdr)); p+=sizeof(hdr);

    uint32_t nchild = hdr.nchild;
    PNode *childs = calloc(nchild, sizeof(*childs));
    for(int i=0; i<nchild; ++i) {
        uint32_t childLen;
        memcpy(&childLen, p, sizeof(childLen)); p+=sizeof(childLen);
        uint8_t *childBlob = malloc(childLen);
        memcpy(childBlob, p, childLen); p+=childLen;
        childs[i] = deserialize(childBlob);
    }
    PNode node = {
        .pid=hdr.pid,
        .nchild=nchild,
        .childs=childs,
    };
    return node;
}

// const int* p -> *p is immutable
// int* const p -> p is immutable
// const int* const p -> both immutable
static char *repeat_char(const char *ch, int count) {
    char *repeated_char = (char*)malloc(strlen(ch)*count);
    repeated_char[0] = '\0';
    for (int i=0; i<count; ++i) {
        strcat(repeated_char, ch);
    }
    return repeated_char;
}

static void displayTree(PNode node, int depth) {
    if (depth != 0)
        printf("|%s ", repeat_char("-", depth));
    printf("My pid (%d)\n", node.pid);
    for (int i=0; i<node.nchild; ++i) {
        displayTree(node.childs[i], depth+1);
    }
}

int main(void) {
    pid_t rootid = getpid();

    createProcess();
    createProcess();
    createProcess();
    // it spawns 8 process

    pid_t pid = getpid();
    // printf("my pid is %u", pid);
    // if (rootid == pid) printf(" (root)");
    // printf("\n");
    
    uint8_t **child_blob = calloc(nchild, sizeof(*child_blob));
    uint32_t *child_len = calloc(nchild, sizeof(*child_len));
    uint32_t payload = 0;
    
    // not leaf node
    for (int i=0; i<nchild; ++i) {
        int ok = recv_blob(c2p_pipes[i][0], &child_blob[i], &child_len[i]);
        close(c2p_pipes[i][0]);
        if (ok <= 0) return 1;
        payload += (uint32_t)sizeof(uint32_t) + child_len[i];
    }

    MsgHdr hdr = {
        .pid=(uint32_t)pid,
        .nchild=(uint32_t)nchild,
        .payload_bytes=payload,
    };
    uint32_t blob_len = (uint32_t)sizeof(MsgHdr) + payload;
    uint8_t *blob = malloc(blob_len);
    uint8_t *p = blob;
    
    memcpy(p, &hdr, sizeof(hdr)); p+=sizeof(hdr);
    for (int i=0; i<nchild; ++i) {
        memcpy(p, &child_len[i], sizeof(uint32_t)); p+=sizeof(uint32_t);
        memcpy(p, child_blob[i], child_len[i]); p+=child_len[i];
        free(child_blob[i]);
    }
    free(child_blob);
    free(child_len); 

    if (rootid != pid) {
        int ok = send_blob(to_parent[1], blob, blob_len);
        close(to_parent[1]);
        if (ok <= 0) {
            printf("send error");
            return 1;
        }
    } else {
        PNode node = deserialize(blob);
        displayTree(node, 0);   
    }

    free(blob);
    return 0;
}

int createProcess() {
    pipe(c2p_pipes[nchild]);
    pid_t pid = fork();

    if (pid < 0) {
        printf("there's some problem!");
        return EXIT_FAILURE;
    }
    if (pid == 0) {
        // this is child
        memcpy(to_parent, c2p_pipes[nchild], sizeof to_parent);
        // memcpy(c2p_pipes, 0, sizeof c2p_pipes);
        close(to_parent[0]);
        nchild = 0;
    } else {
        close(c2p_pipes[nchild][1]);
        nchild++;
    }
    return EXIT_SUCCESS;
}