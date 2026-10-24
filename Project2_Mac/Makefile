CC = clang
CFLAGS = -O3 -g -std=c11 -Wall -Wextra -Werror -pthread

build/bench: src/bench.c
	mkdir -p build
	$(CC) $(CFLAGS) $< -o $@

.PHONY: test run plots
test: build/bench
	./build/bench selftest

run: test
	caffeinate -i .venv/bin/python scripts/run.py

plots:
	.venv/bin/python scripts/analyze.py
