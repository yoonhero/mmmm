#include <errno.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum {
    NODE_ADD,
    NODE_MOVE,
    NODE_OUT,
    NODE_IN,
    NODE_LOOP,
    NODE_CLEAR,
    NODE_MULADD,
    NODE_DEBUG,
} NodeType;

typedef struct Node Node;

typedef struct {
    Node *items;
    size_t len;
    size_t cap;
} NodeVec;

struct Node {
    NodeType type;
    int64_t a;
    int64_t b;
    NodeVec body;
};

static void die(const char *msg) {
    fprintf(stderr, "%s\n", msg);
    exit(1);
}

static void *xcalloc(size_t n, size_t size) {
    void *p = calloc(n, size);
    if (!p) {
        perror("calloc");
        exit(1);
    }
    return p;
}

static void *xrealloc(void *ptr, size_t size) {
    void *p = realloc(ptr, size);
    if (!p) {
        perror("realloc");
        exit(1);
    }
    return p;
}

static void nodevec_init(NodeVec *v) {
    v->items = NULL;
    v->len = 0;
    v->cap = 0;
}

static void nodevec_push(NodeVec *v, Node n) {
    if (v->len == v->cap) {
        size_t new_cap = (v->cap == 0) ? 16 : (v->cap * 2);
        v->items = xrealloc(v->items, new_cap * sizeof(*v->items));
        v->cap = new_cap;
    }
    v->items[v->len++] = n;
}

static void nodevec_free(NodeVec *v);

static void node_destroy(Node *n) {
    if (n->type == NODE_LOOP) {
        nodevec_free(&n->body);
    }
}

static void nodevec_free(NodeVec *v) {
    for (size_t i = 0; i < v->len; i++) {
        node_destroy(&v->items[i]);
    }
    free(v->items);
    v->items = NULL;
    v->len = 0;
    v->cap = 0;
}

static Node make_node(NodeType type, int64_t a, int64_t b) {
    Node n;
    n.type = type;
    n.a = a;
    n.b = b;
    nodevec_init(&n.body);
    return n;
}

static char *read_file(const char *path, size_t *out_len) {
    FILE *fp = fopen(path, "rb");
    if (!fp) {
        fprintf(stderr, "failed to open '%s': %s\n", path, strerror(errno));
        return NULL;
    }

    if (fseek(fp, 0, SEEK_END) != 0) {
        fclose(fp);
        perror("fseek");
        return NULL;
    }

    long sz = ftell(fp);
    if (sz < 0) {
        fclose(fp);
        perror("ftell");
        return NULL;
    }

    if (fseek(fp, 0, SEEK_SET) != 0) {
        fclose(fp);
        perror("fseek");
        return NULL;
    }

    char *buf = xcalloc((size_t)sz + 1, 1);
    if (fread(buf, 1, (size_t)sz, fp) != (size_t)sz) {
        fprintf(stderr, "failed to read '%s'\n", path);
        free(buf);
        fclose(fp);
        return NULL;
    }

    fclose(fp);
    if (out_len) {
        *out_len = (size_t)sz;
    }
    return buf;
}

static bool parse_sequence(const char *src, size_t n, size_t *pos, NodeVec *out, bool in_loop) {
    while (*pos < n) {
        char c = src[*pos];
        if (c == '+' || c == '-') {
            int64_t delta = 0;
            while (*pos < n) {
                char t = src[*pos];
                if (t == '+') {
                    delta++;
                } else if (t == '-') {
                    delta--;
                } else {
                    break;
                }
                (*pos)++;
            }
            if (delta != 0) {
                nodevec_push(out, make_node(NODE_ADD, delta, 0));
            }
            continue;
        }

        if (c == '>' || c == '<') {
            int64_t delta = 0;
            while (*pos < n) {
                char t = src[*pos];
                if (t == '>') {
                    delta++;
                } else if (t == '<') {
                    delta--;
                } else {
                    break;
                }
                (*pos)++;
            }
            if (delta != 0) {
                nodevec_push(out, make_node(NODE_MOVE, delta, 0));
            }
            continue;
        }

        if (c == '.') {
            nodevec_push(out, make_node(NODE_OUT, 0, 0));
            (*pos)++;
            continue;
        }

        if (c == ',') {
            nodevec_push(out, make_node(NODE_IN, 0, 0));
            (*pos)++;
            continue;
        }

        if (c == '#') {
            nodevec_push(out, make_node(NODE_DEBUG, 0, 0));
            (*pos)++;
            continue;
        }

        if (c == '[') {
            (*pos)++;
            Node loop_node = make_node(NODE_LOOP, 0, 0);
            if (!parse_sequence(src, n, pos, &loop_node.body, true)) {
                node_destroy(&loop_node);
                return false;
            }
            nodevec_push(out, loop_node);
            continue;
        }

        if (c == ']') {
            if (!in_loop) {
                fprintf(stderr, "parse error: unmatched ']' at offset %zu\n", *pos);
                return false;
            }
            (*pos)++;
            return true;
        }

        (*pos)++;
    }

    if (in_loop) {
        fprintf(stderr, "parse error: unmatched '[' before end of file\n");
        return false;
    }
    return true;
}

typedef struct {
    int64_t off;
    int64_t delta;
} Delta;

typedef struct {
    Delta *items;
    size_t len;
    size_t cap;
} DeltaVec;

static void deltavec_init(DeltaVec *v) {
    v->items = NULL;
    v->len = 0;
    v->cap = 0;
}

static void deltavec_push(DeltaVec *v, Delta d) {
    if (v->len == v->cap) {
        size_t new_cap = (v->cap == 0) ? 8 : (v->cap * 2);
        v->items = xrealloc(v->items, new_cap * sizeof(*v->items));
        v->cap = new_cap;
    }
    v->items[v->len++] = d;
}

static void deltavec_add(DeltaVec *v, int64_t off, int64_t delta) {
    if (delta == 0) {
        return;
    }

    for (size_t i = 0; i < v->len; i++) {
        if (v->items[i].off == off) {
            v->items[i].delta += delta;
            return;
        }
    }

    Delta d;
    d.off = off;
    d.delta = delta;
    deltavec_push(v, d);
}

static int64_t deltavec_get(const DeltaVec *v, int64_t off) {
    for (size_t i = 0; i < v->len; i++) {
        if (v->items[i].off == off) {
            return v->items[i].delta;
        }
    }
    return 0;
}

static void deltavec_free(DeltaVec *v) {
    free(v->items);
    v->items = NULL;
    v->len = 0;
    v->cap = 0;
}

static bool optimize_loop(const Node *loop_node, NodeVec *replacement) {
    const NodeVec *body = &loop_node->body;

    if (body->len == 1 && body->items[0].type == NODE_ADD) {
        if (body->items[0].a == 1 || body->items[0].a == -1) {
            nodevec_push(replacement, make_node(NODE_CLEAR, 0, 0));
            return true;
        }
    }

    int64_t ptr = 0;
    DeltaVec deltas;
    deltavec_init(&deltas);

    for (size_t i = 0; i < body->len; i++) {
        const Node *n = &body->items[i];
        if (n->type == NODE_MOVE) {
            ptr += n->a;
        } else if (n->type == NODE_ADD) {
            deltavec_add(&deltas, ptr, n->a);
        } else {
            deltavec_free(&deltas);
            return false;
        }
    }

    if (ptr != 0 || deltavec_get(&deltas, 0) != -1) {
        deltavec_free(&deltas);
        return false;
    }

    bool has_target = false;
    for (size_t i = 0; i < deltas.len; i++) {
        int64_t off = deltas.items[i].off;
        int64_t delta = deltas.items[i].delta;
        if (off != 0 && delta != 0) {
            nodevec_push(replacement, make_node(NODE_MULADD, off, delta));
            has_target = true;
        }
    }

    deltavec_free(&deltas);

    if (!has_target) {
        return false;
    }

    nodevec_push(replacement, make_node(NODE_CLEAR, 0, 0));
    return true;
}

static void merge_linear_ops(NodeVec *seq) {
    NodeVec out;
    nodevec_init(&out);

    for (size_t i = 0; i < seq->len; i++) {
        Node n = seq->items[i];

        if ((n.type == NODE_ADD || n.type == NODE_MOVE) && n.a == 0) {
            continue;
        }

        if (out.len > 0) {
            Node *prev = &out.items[out.len - 1];
            if ((n.type == NODE_ADD && prev->type == NODE_ADD) ||
                (n.type == NODE_MOVE && prev->type == NODE_MOVE)) {
                prev->a += n.a;
                if (prev->a == 0) {
                    out.len--;
                }
                continue;
            }
        }

        nodevec_push(&out, n);
    }

    free(seq->items);
    *seq = out;
}

static void optimize_sequence(NodeVec *seq) {
    for (size_t i = 0; i < seq->len; i++) {
        if (seq->items[i].type == NODE_LOOP) {
            optimize_sequence(&seq->items[i].body);
        }
    }

    NodeVec out;
    nodevec_init(&out);

    for (size_t i = 0; i < seq->len; i++) {
        Node n = seq->items[i];
        if (n.type != NODE_LOOP) {
            nodevec_push(&out, n);
            continue;
        }

        NodeVec replacement;
        nodevec_init(&replacement);
        bool replaced = optimize_loop(&n, &replacement);
        if (replaced) {
            for (size_t j = 0; j < replacement.len; j++) {
                nodevec_push(&out, replacement.items[j]);
            }
            free(replacement.items);
            node_destroy(&n);
        } else {
            nodevec_push(&out, n);
            nodevec_free(&replacement);
        }
    }

    free(seq->items);
    *seq = out;

    merge_linear_ops(seq);
}

typedef enum {
    OP_ADD,
    OP_MOVE,
    OP_OUT,
    OP_IN,
    OP_JZ,
    OP_JNZ,
    OP_CLEAR,
    OP_MULADD,
    OP_DEBUG,
} OpType;

typedef struct {
    OpType type;
    int64_t a;
    int64_t b;
} Op;

typedef struct {
    Op *items;
    size_t len;
    size_t cap;
} OpVec;

static void opvec_init(OpVec *v) {
    v->items = NULL;
    v->len = 0;
    v->cap = 0;
}

static size_t opvec_push(OpVec *v, Op op) {
    if (v->len == v->cap) {
        size_t new_cap = (v->cap == 0) ? 32 : (v->cap * 2);
        v->items = xrealloc(v->items, new_cap * sizeof(*v->items));
        v->cap = new_cap;
    }
    v->items[v->len] = op;
    return v->len++;
}

static void emit_program(const NodeVec *seq, OpVec *ops) {
    for (size_t i = 0; i < seq->len; i++) {
        const Node *n = &seq->items[i];
        switch (n->type) {
            case NODE_ADD:
                opvec_push(ops, (Op){OP_ADD, n->a, 0});
                break;
            case NODE_MOVE:
                opvec_push(ops, (Op){OP_MOVE, n->a, 0});
                break;
            case NODE_OUT:
                opvec_push(ops, (Op){OP_OUT, 0, 0});
                break;
            case NODE_IN:
                opvec_push(ops, (Op){OP_IN, 0, 0});
                break;
            case NODE_CLEAR:
                opvec_push(ops, (Op){OP_CLEAR, 0, 0});
                break;
            case NODE_MULADD:
                opvec_push(ops, (Op){OP_MULADD, n->a, n->b});
                break;
            case NODE_DEBUG:
                opvec_push(ops, (Op){OP_DEBUG, 0, 0});
                break;
            case NODE_LOOP: {
                size_t open = opvec_push(ops, (Op){OP_JZ, 0, 0});
                emit_program(&n->body, ops);
                size_t close = opvec_push(ops, (Op){OP_JNZ, (int64_t)open, 0});
                ops->items[open].a = (int64_t)close;
                break;
            }
            default:
                die("internal error: unknown node type");
        }
    }
}

typedef struct {
    uint8_t *cells;
    size_t cap;
    int64_t start;
    int64_t ptr;
    int64_t min_seen;
    int64_t max_seen;
} Tape;

static void tape_init(Tape *t) {
    t->cap = 64;
    t->cells = xcalloc(t->cap, sizeof(*t->cells));
    t->start = -(int64_t)(t->cap / 2);
    t->ptr = 0;
    t->min_seen = 0;
    t->max_seen = 0;
}

static void tape_free(Tape *t) {
    free(t->cells);
    t->cells = NULL;
    t->cap = 0;
}

static void tape_touch(Tape *t, int64_t idx) {
    if (idx < t->min_seen) {
        t->min_seen = idx;
    }
    if (idx > t->max_seen) {
        t->max_seen = idx;
    }
}

static void tape_ensure(Tape *t, int64_t idx) {
    while (idx < t->start || idx >= t->start + (int64_t)t->cap) {
        size_t old_cap = t->cap;
        size_t new_cap = old_cap * 2;
        if (new_cap <= old_cap) {
            die("tape size overflow");
        }

        uint8_t *new_cells = xcalloc(new_cap, sizeof(*new_cells));
        size_t shift = (new_cap - old_cap) / 2;
        memcpy(new_cells + shift, t->cells, old_cap);
        free(t->cells);

        t->cells = new_cells;
        t->cap = new_cap;
        t->start -= (int64_t)shift;
    }
}

static size_t tape_index(const Tape *t, int64_t idx) {
    return (size_t)(idx - t->start);
}

static uint8_t tape_get_at(Tape *t, int64_t idx) {
    tape_ensure(t, idx);
    return t->cells[tape_index(t, idx)];
}

static void tape_set_at(Tape *t, int64_t idx, uint8_t v) {
    tape_ensure(t, idx);
    t->cells[tape_index(t, idx)] = v;
    tape_touch(t, idx);
}

static void tape_add_at(Tape *t, int64_t idx, int64_t delta) {
    tape_ensure(t, idx);
    size_t p = tape_index(t, idx);
    t->cells[p] = (uint8_t)((int64_t)t->cells[p] + delta);
    tape_touch(t, idx);
}

static uint8_t tape_get(Tape *t) {
    return tape_get_at(t, t->ptr);
}

static void tape_set(Tape *t, uint8_t v) {
    tape_set_at(t, t->ptr, v);
}

static void tape_add(Tape *t, int64_t delta) {
    tape_add_at(t, t->ptr, delta);
}

static void tape_move(Tape *t, int64_t delta) {
    t->ptr += delta;
    tape_ensure(t, t->ptr);
    tape_touch(t, t->ptr);
}

static void tape_debug(Tape *t, FILE *out) {
    int64_t shown_from = t->min_seen;
    int64_t shown_to = t->max_seen;
    bool truncated = false;

    int64_t width = shown_to - shown_from + 1;
    const int64_t max_window = 25;
    if (width > (max_window * 2 + 1)) {
        shown_from = t->ptr - max_window;
        shown_to = t->ptr + max_window;
        truncated = true;
    }

    fprintf(out,
            "# ptr=%" PRId64 " cell=%u shown=[%" PRId64 ",%" PRId64 "]%s\n",
            t->ptr,
            (unsigned)tape_get(t),
            shown_from,
            shown_to,
            truncated ? " (truncated)" : "");

    fprintf(out, "# idx :");
    for (int64_t i = shown_from; i <= shown_to; i++) {
        fprintf(out, " %5" PRId64, i);
    }
    fputc('\n', out);

    fprintf(out, "# val :");
    for (int64_t i = shown_from; i <= shown_to; i++) {
        fprintf(out, " %5u", (unsigned)tape_get_at(t, i));
    }
    fputc('\n', out);

    fprintf(out, "# ptr :");
    for (int64_t i = shown_from; i <= shown_to; i++) {
        fprintf(out, " %5s", (i == t->ptr) ? "^" : "");
    }
    fputc('\n', out);
}

static int run_program(const OpVec *ops) {
    Tape tape;
    tape_init(&tape);

    size_t pc = 0;
    while (pc < ops->len) {
        const Op *op = &ops->items[pc];
        switch (op->type) {
            case OP_ADD:
                tape_add(&tape, op->a);
                pc++;
                break;
            case OP_MOVE:
                tape_move(&tape, op->a);
                pc++;
                break;
            case OP_OUT:
                putchar((int)tape_get(&tape));
                pc++;
                break;
            case OP_IN: {
                int c = getchar();
                tape_set(&tape, (c == EOF) ? 0 : (uint8_t)c);
                pc++;
                break;
            }
            case OP_JZ:
                if (tape_get(&tape) == 0) {
                    pc = (size_t)op->a + 1;
                } else {
                    pc++;
                }
                break;
            case OP_JNZ:
                if (tape_get(&tape) != 0) {
                    pc = (size_t)op->a + 1;
                } else {
                    pc++;
                }
                break;
            case OP_CLEAR:
                tape_set(&tape, 0);
                pc++;
                break;
            case OP_MULADD: {
                uint8_t v = tape_get(&tape);
                if (v != 0) {
                    tape_add_at(&tape, tape.ptr + op->a, (int64_t)v * op->b);
                }
                pc++;
                break;
            }
            case OP_DEBUG:
                tape_debug(&tape, stderr);
                pc++;
                break;
            default:
                die("internal error: unknown opcode");
        }
    }

    tape_free(&tape);
    return 0;
}

static void print_usage(const char *argv0) {
    fprintf(stderr, "Usage: %s <source.bf>\n", argv0);
}

int main(int argc, char **argv) {
    if (argc != 2) {
        print_usage(argv[0]);
        return 1;
    }

    size_t src_len = 0;
    char *src = read_file(argv[1], &src_len);
    if (!src) {
        return 1;
    }

    NodeVec ast;
    nodevec_init(&ast);

    size_t pos = 0;
    if (!parse_sequence(src, src_len, &pos, &ast, false)) {
        nodevec_free(&ast);
        free(src);
        return 1;
    }

    optimize_sequence(&ast);

    OpVec ops;
    opvec_init(&ops);
    emit_program(&ast, &ops);

    int rc = run_program(&ops);

    free(ops.items);
    nodevec_free(&ast);
    free(src);
    return rc;
}
