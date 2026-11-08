# Student Test Suite & Validation Fixtures

This directory contains our comprehensive student test suite and empirical benchmark results covering all edge cases, boundary conditions, and stress tests for Assignment 4.

## Files

- `fixtures.json`: Contains 32 curated student test cases across all eight algorithm tasks (`lcs`, `merge`, `tree`, `naive`, `kmp`, `rk`, `suffix`, `aho`). Each entry records the test name, input request, expected output, actual output, status (`PASS`), and the specific algorithmic defect it checks.
- `student_tests.jsonl`: Clean UTF-8 JSON Lines input containing all student test requests for verification via `--input`.
- `benchmarks.json`: Raw empirical timing data (5 runs per algorithm/size/case, medians, match counts) comparing `naive`, `kmp`, and `rk` on identical datasets across random and repetitive inputs.

## Running Student Tests

To run the student test suite and regenerate the benchmark measurements:

```sh
python tools/student_test_and_benchmark.py
```

To run the student requests directly through the assignment runner:

```sh
python tools/run.py --input tests/student/student_tests.jsonl
```
