#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static double seconds(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t)) {
        perror("clock_gettime");
        exit(1);
    }
    return t.tv_sec + t.tv_nsec * 1e-9;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s cache|memory|tlb-local|tlb-spread\n", argv[0]);
        return 1;
    }
    size_t count, stride;
    if (!strcmp(argv[1], "cache")) {
        count = 256; stride = 128;
    } else if (!strcmp(argv[1], "memory")) {
        count = 524288; stride = 128;
    } else if (!strcmp(argv[1], "tlb-local")) {
        count = 8192; stride = 128;
    } else if (!strcmp(argv[1], "tlb-spread")) {
        /* Same-page offsets also introduce cache conflicts; this is not an isolated TLB test. */
        count = 8192; stride = 16384;
    } else {
        fprintf(stderr, "Unknown mode: %s\n", argv[1]);
        return 1;
    }
    unsigned char *data = NULL;
    size_t *order = malloc(count * sizeof(*order));
    if (posix_memalign((void **)&data, 16384, count * stride) || !order) {
        fprintf(stderr, "Allocation failed\n");
        free(data); free(order);
        return 1;
    }
    for (size_t i = 0; i < count; i++) order[i] = i;
    uint64_t random = 42;
    for (size_t i = count - 1; i > 0; i--) {
        random ^= random << 13; random ^= random >> 7; random ^= random << 17;
        size_t j = random % (i + 1), tmp = order[i];
        order[i] = order[j]; order[j] = tmp;
    }
    for (size_t i = 0; i < count; i++)
        *(size_t *)(data + order[i] * stride) = order[(i + 1) % count] * stride;
    size_t offset = order[0] * stride, start = offset;
    for (size_t i = 0; i < count; i++) {
        assert(offset < count * stride && offset % stride == 0);
        offset = *(size_t *)(data + offset);
        assert(i + 1 == count || offset != start);
    }
    assert(offset == start);
    free(order);
    uint64_t loads = 0;
    double begin = seconds(), end;
    do {
        for (size_t i = 0; i < 65536; i++) offset = *(size_t *)(data + offset);
        loads += 65536;
        end = seconds();
    } while (end - begin < 2.0);
    printf("mode=%s bytes=%zu nodes=%zu stride=%zu loads=%llu seconds=%.6f ns_per_load=%.3f checksum=%zu\n",
           argv[1], count * stride, count, stride, (unsigned long long)loads,
           end - begin, (end - begin) * 1e9 / loads, offset);
    free(data);
    return 0;
}
