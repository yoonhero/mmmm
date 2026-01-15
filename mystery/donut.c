#include <stdio.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include <stdlib.h>

static long now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000L + ts.tv_nsec / 1000000L;
}

#define max(a, b) ((a)>(b)?(a):(b))
#define min(a, b) ((a)>(b)?(b):(a))
int clip(int n, int lb, int ub) {
    return max(lb, min(n, ub));
}

char shade[] = " .,-~:;=!*#$@";

#define WIDTH 64
#define HEIGHT 64
typedef struct Frame {
    int data[WIDTH][HEIGHT];
    long prevRendered; 
} Frame;

void renderFrame(Frame *frame){
    printf("\033[2J\033[H");
    fflush(stdout);
    for (int y = 0; y < HEIGHT; ++y) {
        for (int x = 0; x < WIDTH; ++x) {
            putchar(shade[frame->data[x][y]]);
        }
        putchar('\n');
    }
}

typedef struct Point {
    int x;
    int y;
} Point;

typedef struct ScreenPoint {
    Point pt;
    int bright;
} ScreenPoint;

typedef struct Vec3d {
    double x;
    double y;
    double z;
} Vec3d;

typedef struct {
    Vec3d *data;
    size_t len;
} Vec3Buf; // more safe design@

static Vec3Buf vec3bufAlloc(size_t len) {
    Vec3Buf b = {0};
    b.data = malloc(len * sizeof *b.data);
    if (!b.data) return (Vec3Buf){0};
    b.len = len;
    return b;
}

static void vec3bufFree(Vec3Buf *b) {
    if (!b) return;
    free(b->data);
    b->data = NULL;
    b->len = 0;
}

void point(Frame *frame, ScreenPoint screenPt) {
    Point pt = screenPt.pt;
    if (0 <= pt.x && pt.x < WIDTH && 0 <= pt.y && pt.y < HEIGHT) {
        frame->data[pt.x][pt.y] = max(frame->data[pt.x][pt.y], screenPt.bright);
    }
}

ScreenPoint screen(Vec3d pt) {
    ScreenPoint screenPt = (ScreenPoint){0};
    size_t totalShade = strlen(shade);
    pt.x = (pt.x+1)/2 * WIDTH;
    pt.y = (1-(pt.y+1)/2) * HEIGHT;
    screenPt.pt.x = (int)floor(pt.x);
    screenPt.pt.y = (int)floor(pt.y);
    screenPt.bright = clip((int)floor((1-pt.z/2)*totalShade), 0, totalShade-1);
    return screenPt;
}

Vec3d project(Vec3d pt) {
    pt.z++; // camera on (0, 0, -1)
    pt.x = pt.x/pt.z;
    pt.y = pt.y/pt.z;
    return pt;
}

Vec3d vec3PointMul(Vec3d pt, double scale) {
    pt.x *= scale;
    pt.y *= scale;
    pt.z *= scale;
    return pt;
}

double square(double x) {
    return pow(x, 2);
}

Vec3d vec3Normalize(Vec3d pt) {
    double norm = sqrt(square(pt.x)+square(pt.y)+square(pt.z));
    return vec3PointMul(pt, 1/norm);
}

Vec3d vec3Cross(Vec3d pt1, Vec3d pt2){
    Vec3d n = {
        .x = pt1.y*pt2.z-pt1.z*pt2.y,
        .y = -(pt1.x*pt2.z-pt1.z*pt2.x),
        .z = pt1.x*pt2.y-pt1.y*pt2.x
    };
    return n;
}

Vec3d solveEq(Vec3d normal) {
    Vec3d v = {1, 1, 1};
    if (normal.x != 0) {
        v.x = (-normal.y-normal.z)/normal.x;
    } else if (normal.z != 0) {
        v.z = (-normal.x-normal.y)/normal.z;
    } else {
        v.y = (-normal.x-normal.z)/normal.y;
    }

    return v;
}

Vec3d polarCoord(Vec3d origin, Vec3d orientation, double t, double radius){
    Vec3d u1 = vec3Normalize(solveEq(orientation));
    Vec3d u2 = vec3Normalize(vec3Cross(orientation, u1));
    u1 = vec3PointMul(u1, radius * cos(2.0*M_PI*t));
    u2 = vec3PointMul(u2, radius * sin(2.0*M_PI*t));
    
    Vec3d pt = {
        .x = origin.x + u1.x + u2.x,
        .y = origin.y + u1.y + u2.y, 
        .z = origin.z + u1.z + u2.z
    };
    return pt;
}

Vec3d sphereCoord(double theta, double phi) {
    Vec3d pt = {
        .x = sin(phi) * cos(theta),
        .y = sin(phi) * sin(theta),
        .z = cos(phi)
    };
    return pt;
}

// Bad Design
// Vec3d *makeCircle(Vec3d origin, Vec3d orientation, int N){
//     Vec3d *points = malloc(N * sizeof(*points));
//     if (!points) return NULL;

//     for (int i = 0; i<N; ++i) {
//         double t = (double)i / N;
//         Vec3d pt = polarCoord(origin, orientation, t, 0.2);
//         points[i] = pt;
//     }
//     return points;
// }

static int fillDonut(Vec3Buf buf, Vec3d origin, Vec3d orientation, int N, int M) {
    size_t need = (size_t)N * (size_t)M;
    if (!buf.data || buf.len < need) return 0;

    for (int i = 0; i<N; ++i) {
        double t = (double)i / N;
        Vec3d circleOrigin = polarCoord(origin, orientation, t, 0.5);
        Vec3d normalVec = vec3Normalize(vec3Cross(orientation, circleOrigin));

        for (int j = 0; j < M; ++j) {
            double s = (double)j / M;
            Vec3d pt = polarCoord(circleOrigin, normalVec, s, 0.2);
            buf.data[(size_t)i * (size_t)M + (size_t)j] = pt;
        }
    } 
    return 1;
}

int main() {
    const int resetData[WIDTH][HEIGHT] = {};
    Frame *frame = malloc(sizeof(Frame)); // calloc(1, sizeof *frame)
    *frame = (Frame){0};

    float fps = 15.0;
    long targetDt = 1000/fps;

    Vec3d origin = {0, 0, 0};
    double theta = 0;
    double phi = 0;
    const size_t N = 128;
    const size_t M = 128;
    const size_t totalPoints = N*M;
    Vec3Buf pts = vec3bufAlloc(totalPoints);

    while (1) {
        long current = now_ms();
        long dt = current - frame->prevRendered;
        if (dt < targetDt) {
            continue;
        }
        frame->prevRendered = current;

        theta += (double)dt / 1000;
        phi += (double)dt / 1000;
        
        Vec3d orientation = sphereCoord(theta, phi);
        if (!fillDonut(pts, origin, orientation, N, M)) {
            vec3bufFree(&pts);
            return 1;
        }
        for (int i=0; i<totalPoints; ++i) {
            point(frame, screen(project(pts.data[i])));
        }

        renderFrame(frame);
        memset(frame->data, 0, sizeof frame->data);
    }

    vec3bufFree(&pts);
    free(frame);
    return 0;
}