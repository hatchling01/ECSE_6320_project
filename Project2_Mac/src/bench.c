#define _POSIX_C_SOURCE 200809L
#define _DARWIN_C_SOURCE
#include <assert.h>
#include <errno.h>
#include <math.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#ifdef __APPLE__
#include <os/signpost.h>
#include <pthread/qos.h>
#endif

static volatile uint64_t sink;
#ifdef __APPLE__
static os_log_t log_handle;
static os_signpost_id_t signpost;
#endif

static void fail(const char *s) { fprintf(stderr, "%s\n", s); exit(1); }
static void check_thread(int rc) { if (rc) { errno = rc; perror("pthread"); exit(1); } }
static double now(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t)) { perror("clock_gettime"); exit(1); }
    return t.tv_sec + t.tv_nsec * 1e-9;
}
static void begin_region(void) {
#ifdef __APPLE__
    os_signpost_interval_begin(log_handle, signpost, "Measurement");
#endif
}
static void end_region(void) {
#ifdef __APPLE__
    os_signpost_interval_end(log_handle, signpost, "Measurement");
#endif
}
static uint64_t number(const char *s) {
    char *end;
    errno = 0;
    unsigned long long n = strtoull(s, &end, 10);
    if (errno || !*s || *end || s[0] == '-') fail("Invalid unsigned integer");
    return n;
}
static double duration(const char *s) {
    char *end;
    double v = strtod(s, &end);
    if (!*s || *end || !isfinite(v) || v < 0.01 || v > 30) fail("Duration must be 0.01..30 seconds");
    return v;
}
static void *allocate(size_t bytes) {
    void *p = NULL;
    if (!bytes || bytes > (size_t)2 * 1024 * 1024 * 1024) fail("Allocation outside 1 byte..2 GiB");
    if (posix_memalign(&p, (size_t)sysconf(_SC_PAGESIZE), bytes)) fail("Allocation failed");
    memset(p, 0, bytes);
    return p;
}
static uint64_t rng(uint64_t *s) {
    *s ^= *s << 13; *s ^= *s >> 7; *s ^= *s << 17;
    return *s;
}
static size_t *permutation(size_t n, uint64_t seed) {
    size_t *p = allocate(n * sizeof(*p));
    for (size_t i = 0; i < n; i++) p[i] = i;
    if (seed) for (size_t i = n - 1; i; i--) {
        size_t j = rng(&seed) % (i + 1), t = p[i]; p[i] = p[j]; p[j] = t;
    }
    return p;
}
static size_t location(size_t i, size_t stride, int spread) {
    /* Rotate the line offset to avoid concentrating every page in one L1 set. */
    return i * stride + (spread ? ((i * 37) % (stride / 128)) * 128 : 0);
}
static unsigned char *ring(size_t bytes, size_t stride, uint64_t seed, int spread) {
    if (stride < 8 || stride % 8 || bytes % stride || bytes / stride < 2)
        fail("Ring requires aligned stride and at least two nodes");
    if (spread && (stride < 128 || stride % 128)) fail("Invalid page stride");
    size_t n = bytes / stride;
    unsigned char *p = allocate(bytes);
    size_t *order = permutation(n, seed);
    for (size_t i = 0; i < n; i++)
        *(size_t *)(p + location(order[i], stride, spread)) = location(order[(i + 1) % n], stride, spread);
    size_t offset = location(order[0], stride, spread), first = offset;
    for (size_t i = 0; i < n; i++) {
        assert(offset < bytes && offset % 8 == 0);
        offset = *(size_t *)(p + offset);
        assert(i + 1 == n || offset != first);
    }
    assert(offset == first);
    /* All layouts contain node zero at offset zero. */
    free(order);
    return p;
}
static size_t chase(unsigned char *p, size_t offset, size_t count) {
    for (size_t i = 0; i < count; i++) offset = *(size_t *)(p + offset);
    return offset;
}
static uint64_t pass(uint64_t *p, const size_t *order, size_t count, size_t step,
                     int reads, uint64_t salt) {
    uint64_t sum = 0;
    if (reads == 100) {
        for (size_t i = 0; i < count; i++) sum += p[(order ? order[i] : i) * step];
    } else if (reads == 0) {
        for (size_t i = 0; i < count; i++) p[(order ? order[i] : i) * step] = salt;
    } else {
        size_t i = 0;
        const size_t r = (size_t)reads / 10;
        for (; i + 10 <= count; i += 10) {
            for (size_t k = 0; k < r; k++) sum += p[(order ? order[i + k] : i + k) * step];
            for (size_t k = r; k < 10; k++) p[(order ? order[i + k] : i + k) * step] = salt;
        }
        for (; i < count; i++) {
            size_t j = (order ? order[i] : i) * step;
            if (i % 10 < r) sum += p[j]; else p[j] = salt;
        }
    }
    /* Prevent eliminating earlier write passes whose values are later overwritten. */
    __asm__ volatile("" : : "r"(sum), "r"(p) : "memory");
    return sum;
}
static void print_result(const char *mode, size_t bytes, size_t stride, int reads,
                         int workers, uint64_t ops, double elapsed, double bandwidth,
                         double bg_bandwidth, double probe_ns, uint64_t checksum) {
    printf("{\"mode\":\"%s\",\"bytes\":%zu,\"stride\":%zu,\"read_percent\":%d,"
           "\"workers\":%d,\"operations\":%llu,\"seconds\":%.9f,\"ns_per_op\":%.6f,"
           "\"useful_GB_s\":%.6f,\"background_GB_s\":%.6f,\"probe_ns\":%.6f,\"checksum\":%llu}\n",
           mode, bytes, stride, reads, workers, (unsigned long long)ops, elapsed,
           elapsed * 1e9 / ops, bandwidth, bg_bandwidth, probe_ns, (unsigned long long)checksum);
}

struct load {
    pthread_mutex_t mutex;
    pthread_cond_t cond;
    int ready, start;
    atomic_int stop;
    int reads;
};
struct worker { struct load *shared; uint64_t *data, ops, checksum; double end; };
static void *background(void *arg) {
    struct worker *w = arg;
    struct load *s = w->shared;
#ifdef __APPLE__
    (void)pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
#endif
    check_thread(pthread_mutex_lock(&s->mutex));
    s->ready++; check_thread(pthread_cond_broadcast(&s->cond));
    while (!s->start) check_thread(pthread_cond_wait(&s->cond, &s->mutex));
    check_thread(pthread_mutex_unlock(&s->mutex));
    size_t offset = 0;
    const size_t chunk = 65536, count = 128 * 1024 * 1024 / sizeof(uint64_t);
    while (!atomic_load_explicit(&s->stop, memory_order_relaxed)) {
        w->checksum += pass(w->data + offset, NULL, chunk, 1, s->reads, w->ops + 1);
        w->ops += chunk;
        offset = (offset + chunk) % count;
    }
    atomic_thread_fence(memory_order_seq_cst);
    w->end = now();
    return NULL;
}
static void loaded(int count, int reads, double seconds, uint64_t seed) {
    if (count < 0 || count > 11) fail("Workers must be 0..11");
    const size_t bytes = 256 * 1024 * 1024;
    unsigned char *p = ring(bytes, 128, seed, 0);
    size_t offset = chase(p, 0, bytes / 128);
    struct load shared = {.mutex = PTHREAD_MUTEX_INITIALIZER, .cond = PTHREAD_COND_INITIALIZER,
                          .ready = 0, .start = 0, .stop = ATOMIC_VAR_INIT(0), .reads = reads};
    struct worker workers[11] = {0};
    pthread_t threads[11];
    for (int i = 0; i < count; i++) {
        workers[i].shared = &shared;
        workers[i].data = allocate(128 * 1024 * 1024);
        check_thread(pthread_create(&threads[i], NULL, background, &workers[i]));
    }
    check_thread(pthread_mutex_lock(&shared.mutex));
    while (shared.ready != count) check_thread(pthread_cond_wait(&shared.cond, &shared.mutex));
    begin_region();
    double start = now();
    shared.start = 1; check_thread(pthread_cond_broadcast(&shared.cond));
    check_thread(pthread_mutex_unlock(&shared.mutex));
    uint64_t ops = 0, bg_ops = 0;
    double end;
    do { offset = chase(p, offset, 4096); ops += 4096; end = now(); } while (end - start < seconds);
    atomic_store_explicit(&shared.stop, 1, memory_order_relaxed);
    double finish = end;
    for (int i = 0; i < count; i++) {
        check_thread(pthread_join(threads[i], NULL));
        bg_ops += workers[i].ops;
        if (workers[i].end > finish) finish = workers[i].end;
        sink ^= workers[i].checksum;
        free(workers[i].data);
    }
    end_region();
    sink ^= offset;
    print_result("loaded", bytes, 128, reads, count, ops, end - start,
                 ops * 8.0 / (end - start) / 1e9, bg_ops * 8.0 / (finish - start) / 1e9,
                 (end - start) * 1e9 / ops, offset);
    free(p);
    check_thread(pthread_cond_destroy(&shared.cond)); check_thread(pthread_mutex_destroy(&shared.mutex));
}
static void kernel(size_t bytes, size_t stride, double seconds) {
    if (bytes % 24 || stride % 8 || !stride) fail("Kernel bytes must be divisible by 24; stride by 8");
    size_t n = bytes / 24, step = stride / 8;
    if (!n || step > n) fail("Invalid kernel size");
    double *x = allocate(n * 8), *y = allocate(n * 8), *z = allocate(n * 8);
    for (size_t i = 0; i < n; i++) { x[i] = (double)(i % 17); y[i] = 0.5; }
    for (size_t i = 0; i < n; i += step) z[i] = x[i] * y[i];
    uint64_t ops = 0;
    begin_region(); double start = now(), end;
    do {
        for (size_t i = 0; i < n; i += step) z[i] = x[i] * y[i];
        __asm__ volatile("" : : "r"(z) : "memory");
        ops += (n + step - 1) / step; end = now();
    } while (end - start < seconds);
    end_region();
    uint64_t checksum = 0;
    for (size_t i = 0; i < n; i += step) { assert(z[i] == (double)(i % 17) * 0.5); checksum += (uint64_t)(z[i] * 2); }
    sink ^= checksum;
    print_result("multiply", bytes, stride, 67, 0, ops, end - start,
                 ops * 24.0 / (end - start) / 1e9, 0, 0, checksum);
    free(x); free(y); free(z);
}
static void selftest(void) {
    for (int reads = 0; reads <= 100; reads += 10) {
        if (reads != 0 && reads != 50 && reads != 70 && reads != 100) continue;
        for (int random = 0; random <= 1; random++) {
            uint64_t data[37], expected[37];
            size_t *order = random ? permutation(37, 42) : NULL;
            uint64_t sum = 0;
            for (size_t i = 0; i < 37; i++) data[i] = expected[i] = i + 1;
            for (size_t i = 0; i < 37; i++) {
                size_t j = order ? order[i] : i;
                if ((int)(i % 10) < reads / 10) sum += expected[j]; else expected[j] = 99;
            }
            assert(pass(data, order, 37, 1, reads, 99) == sum);
            assert(!memcmp(data, expected, sizeof(data)));
            free(order);
        }
    }
    for (int spread = 0; spread <= 1; spread++) {
        size_t stride = spread ? 16384 : 128;
        unsigned char *p = ring(32 * stride, stride, 42, spread);
        assert(chase(p, 0, 32) == 0);
        free(p);
    }
    kernel(24 * 128, 8, 0.01);
    puts("{\"selftest\":\"passed\"}");
}
int main(int argc, char **argv) {
#ifdef __APPLE__
    log_handle = os_log_create("edu.ecse.memory", OS_LOG_CATEGORY_POINTS_OF_INTEREST);
    signpost = os_signpost_id_generate(log_handle);
    int qos_rc = pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
    if (qos_rc) fprintf(stderr, "QoS request failed: %d\n", qos_rc);
#endif
    if (argc == 2 && !strcmp(argv[1], "selftest")) { selftest(); return 0; }
    if (argc == 6 && !strcmp(argv[1], "loaded")) {
        uint64_t count = number(argv[2]), reads = number(argv[3]);
        if (count > 11 || (reads != 0 && reads != 50 && reads != 70 && reads != 100)) fail("Invalid workers or mix");
        uint64_t seed = number(argv[5]); if (!seed) fail("Loaded probe needs a nonzero random seed");
        loaded((int)count, (int)reads, duration(argv[4]), seed); return 0;
    }
    if (argc == 5 && !strcmp(argv[1], "kernel")) {
        kernel(number(argv[2]), number(argv[3]), duration(argv[4])); return 0;
    }
    if (argc != 8) fail("Usage: bench chase|pages|stream bytes stride sequential|random read_percent seconds seed; bench loaded workers read_percent seconds seed; bench kernel total_bytes stride seconds; bench selftest");
    size_t bytes = number(argv[2]), stride = number(argv[3]);
    if (bytes > (size_t)2 * 1024 * 1024 * 1024 || stride < 8 || stride % 8 || bytes % stride || bytes / stride < 2)
        fail("Invalid footprint/stride");
    int random = !strcmp(argv[4], "random");
    if (!random && strcmp(argv[4], "sequential")) fail("Invalid access pattern");
    uint64_t reads = number(argv[5]), seed = number(argv[7]);
    if (reads != 0 && reads != 50 && reads != 70 && reads != 100) fail("Unsupported read percentage");
    if (!seed) fail("Seed must be nonzero");
    double seconds = duration(argv[6]);
    if (!strcmp(argv[1], "chase") || !strcmp(argv[1], "pages")) {
        int spread = !strcmp(argv[1], "pages");
        if (reads != 100) fail("Pointer chasing is read-only");
        unsigned char *p = ring(bytes, stride, random ? seed : 0, spread);
        size_t offset = chase(p, 0, bytes / stride);
        uint64_t ops = 0;
        begin_region(); double start = now(), end;
        do { offset = chase(p, offset, 4096); ops += 4096; end = now(); } while (end - start < seconds);
        end_region(); sink ^= offset;
        print_result(argv[1], bytes, stride, 100, 0, ops, end - start, ops * 8.0 / (end - start) / 1e9, 0, 0, offset);
        free(p);
    } else if (!strcmp(argv[1], "stream")) {
        size_t count = bytes / stride;
        uint64_t *p = allocate(bytes), checksum = 0, ops = 0, passes = 0;
        size_t *order = random ? permutation(count, seed) : NULL;
        for (size_t i = 0; i < bytes / 8; i++) p[i] = i + 1;
        checksum ^= pass(p, order, count, stride / 8, (int)reads, 1);
        begin_region(); double start = now(), end;
        do {
            checksum += pass(p, order, count, stride / 8, (int)reads, ++passes);
            ops += count; end = now();
        } while (end - start < seconds);
        atomic_thread_fence(memory_order_seq_cst); end = now(); end_region();
        /* Validate writes and consume output outside the timed region. */
        if (!reads) assert(p[0] == passes);
        sink ^= checksum ^ p[0];
        print_result("stream", bytes, stride, (int)reads, 0, ops, end - start,
                     ops * 8.0 / (end - start) / 1e9, 0, 0, checksum ^ p[0]);
        free(order); free(p);
    } else fail("Unknown benchmark mode");
    return 0;
}
