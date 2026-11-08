"""Student test suite verification and string search empirical benchmark.

Generates student test fixtures, tests them against the algorithm implementations,
and conducts reproducible benchmarks across three increasing sizes for Naive, KMP, and RK.
"""

import json
import random
import sys
import time
from pathlib import Path

# Add Python/source and tools to path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "Python" / "source"))
sys.path.insert(0, str(repo_root / "tools"))

import algorithms
from public_validate import check


def create_student_tests():
    """Create a rich suite of student tests covering every command and edge condition."""
    tests = [
        # --- LCS ---
        {
            "name": "lcs-both-empty",
            "input": {"task": "lcs", "a": "", "b": ""},
            "output": {"length": 0, "sequence": ""},
            "defect": "Failure to handle empty strings or returning null instead of empty sequence",
        },
        {
            "name": "lcs-one-empty",
            "input": {"task": "lcs", "a": "algorithm", "b": ""},
            "output": {"length": 0, "sequence": ""},
            "defect": "Unchecked index bounds when one string has length 0",
        },
        {
            "name": "lcs-interleaved-subsequence",
            "input": {"task": "lcs", "a": "XAYBZCD", "b": "1A2B3C4D5"},
            "output": {"length": 4, "sequence": "ABCD"},
            "defect": "Erroneously requiring contiguous characters (substring instead of subsequence)",
        },
        {
            "name": "lcs-repeated-characters",
            "input": {"task": "lcs", "a": "AAAA", "b": "AA"},
            "output": {"length": 2, "sequence": "AA"},
            "defect": "Duplicate character overcounting or incorrect pointer decrement",
        },
        {
            "name": "lcs-alternative-optimal",
            "input": {"task": "lcs", "a": "AB", "b": "BA"},
            "output": {"length": 1, "sequence": "A"},  # "B" is also valid
            "defect": "Tie-breaking mishandling in DP reconstruction leading to length/sequence mismatch",
        },

        # --- MERGE ---
        {
            "name": "merge-empty",
            "input": {"task": "merge", "sizes": []},
            "output": {"cost": 0, "plan": []},
            "defect": "IndexError on empty array or nonzero cost for zero blocks",
        },
        {
            "name": "merge-single-block",
            "input": {"task": "merge", "sizes": [42]},
            "output": {"cost": 0, "plan": []},
            "defect": "Emitting unnecessary merges or non-zero cost when no merges are needed",
        },
        {
            "name": "merge-with-zeros",
            "input": {"task": "merge", "sizes": [0, 5, 0, 5]},
            "output": {"cost": 20, "plan": [[0, 0, 1], [2, 2, 3], [0, 1, 3]]},
            "defect": "Mishandling zero-sized blocks during interval cost summation",
        },
        {
            "name": "merge-adjacent-vs-arbitrary",
            "input": {"task": "merge", "sizes": [10, 100, 10]},
            # If arbitrary greedy: merge 10+10=20, total 20+120=140. But 10 and 10 are not adjacent!
            # Adjacent choices:
            # Option 1: (10+100) + ((10+100)+10) = 110 + 120 = 230.
            # Option 2: (100+10) + (10+(100+10)) = 110 + 120 = 230.
            "output": {"cost": 230, "plan": [[0, 0, 1], [0, 1, 2]]},
            "defect": "Greedily picking non-adjacent minimum blocks instead of adhering to adjacency",
        },
        {
            "name": "merge-large-costs-64bit",
            "input": {"task": "merge", "sizes": [1000000000, 1000000000, 1000000000]},
            "output": {"cost": 5000000000, "plan": [[0, 0, 1], [0, 1, 2]]},
            "defect": "32-bit integer overflow when cumulative merge cost exceeds 2^31 - 1",
        },

        # --- TREE ---
        {
            "name": "tree-empty",
            "input": {"task": "tree", "n": 0, "weights": [], "edges": []},
            "output": {"weight": 0, "selected": []},
            "defect": "IndexError on empty tree initialization",
        },
        {
            "name": "tree-single-negative",
            "input": {"task": "tree", "n": 1, "weights": [-15], "edges": []},
            "output": {"weight": 0, "selected": []},
            "defect": "Selecting negative vertex when empty set (weight 0) is permitted and superior",
        },
        {
            "name": "tree-all-negative",
            "input": {"task": "tree", "n": 3, "weights": [-5, -10, -2], "edges": [[0, 1], [1, 2]]},
            "output": {"weight": 0, "selected": []},
            "defect": "Selecting any vertex in all-negative tree instead of optimal empty set",
        },
        {
            "name": "tree-deep-chain",
            "input": {
                "task": "tree",
                "n": 6,
                "weights": [10, 1, 10, 1, 10, 1],
                "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]],
            },
            "output": {"weight": 30, "selected": [0, 2, 4]},
            "defect": "Recursion limit exhaustion or picking adjacent vertices along chain",
        },
        {
            "name": "tree-star-center-vs-leaves",
            "input": {
                "task": "tree",
                "n": 5,
                "weights": [15, 5, 5, 5, 5],
                "edges": [[0, 1], [0, 2], [0, 3], [0, 4]],
            },
            "output": {"weight": 20, "selected": [1, 2, 3, 4]},
            "defect": "Greedily picking center node with highest individual weight over sum of leaves",
        },

        # --- NAIVE / KMP / RK ---
        {
            "name": "search-empty-pattern",
            "input": {"task": "naive", "text": "hello", "pattern": ""},
            "output": {"positions": [0, 1, 2, 3, 4, 5]},
            "defect": "Failing to return all n+1 boundary start positions for empty pattern",
        },
        {
            "name": "search-pattern-longer",
            "input": {"task": "kmp", "text": "abc", "pattern": "abcdef"},
            "output": {"positions": []},
            "defect": "Index out of bounds or false positives when pattern length > text length",
        },
        {
            "name": "search-overlapping",
            "input": {"task": "kmp", "text": "AAAA", "pattern": "AA"},
            "output": {"positions": [0, 1, 2]},
            "defect": "Skipping overlapping occurrences by advancing text index past match end",
        },
        {
            "name": "search-case-and-punctuation",
            "input": {"task": "naive", "text": "Test! test? Test!", "pattern": "Test!"},
            "output": {"positions": [0, 12]},
            "defect": "Unintended case-folding or punctuation stripping violating ASCII exact match",
        },
        {
            "name": "rk-hash-collision-verification",
            "input": {"task": "rk", "text": "abdj", "pattern": "ab"},
            "output": {"positions": [0]},
            "defect": "Reporting candidate 'dj' as match because hash('ab') == hash('dj') == 75 mod 101",
        },
        {
            "name": "rk-negative-modulo-normalization",
            "input": {"task": "rk", "text": "zabcdef", "pattern": "bcd"},
            "output": {"positions": [2]},
            "defect": "Un-normalized negative remainders causing hash lookup mismatch during sliding roll",
        },

        # --- SUFFIX ARRAY & KASAI LCP ---
        {
            "name": "suffix-empty",
            "input": {"task": "suffix", "text": ""},
            "output": {"sa": [], "lcp": [], "repeated": ""},
            "defect": "Crash on empty text or returning [0] instead of empty array",
        },
        {
            "name": "suffix-single-char",
            "input": {"task": "suffix", "text": "x"},
            "output": {"sa": [0], "lcp": [0], "repeated": ""},
            "defect": "Crash on single character or identifying single character as repeated",
        },
        {
            "name": "suffix-all-identical",
            "input": {"task": "suffix", "text": "aaaa"},
            "output": {"sa": [3, 2, 1, 0], "lcp": [0, 1, 2, 3], "repeated": "aaa"},
            "defect": "Incorrect suffix ordering or failing to detect overlapping maximal repeat",
        },
        {
            "name": "suffix-all-distinct",
            "input": {"task": "suffix", "text": "abcdef"},
            "output": {"sa": [0, 1, 2, 3, 4, 5], "lcp": [0, 0, 0, 0, 0, 0], "repeated": ""},
            "defect": "False non-empty repeated string when no character repeats",
        },
        {
            "name": "suffix-tie-longest-repeats",
            "input": {"task": "suffix", "text": "xyz_xyz_abc_abc"},
            "output": {
                "sa": [11, 7, 3, 12, 8, 13, 9, 14, 10, 4, 0, 5, 1, 6, 2],
                "lcp": [0, 4, 1, 0, 3, 0, 2, 0, 1, 0, 4, 0, 3, 0, 2],
                "repeated": "_abc",
            },
            "defect": "Failure to accurately compute SA/LCP or select maximal length repeat when multiple repeats exist",
        },

        # --- AHO-CORASICK ---
        {
            "name": "aho-empty-dictionary",
            "input": {"task": "aho", "patterns": [], "texts": ["sample", "text"]},
            "output": {"counts": [[], []]},
            "defect": "Crash on empty dictionary or non-empty count row",
        },
        {
            "name": "aho-empty-texts",
            "input": {"task": "aho", "patterns": ["pattern"], "texts": []},
            "output": {"counts": []},
            "defect": "Crash on empty texts array or returning non-empty list",
        },
        {
            "name": "aho-empty-text-string",
            "input": {"task": "aho", "patterns": ["alpha", "beta"], "texts": ["", "alpha"]},
            "output": {"counts": [[0, 0], [1, 0]]},
            "defect": "Failure to output zero count row for empty text string",
        },
        {
            "name": "aho-duplicate-patterns",
            "input": {"task": "aho", "patterns": ["test", "test"], "texts": ["test test"]},
            "output": {"counts": [[2, 2]]},
            "defect": "Overwriting duplicate pattern entries instead of giving each its full count",
        },
        {
            "name": "aho-nested-suffix-patterns",
            "input": {"task": "aho", "patterns": ["she", "he", "hers"], "texts": ["ushers"]},
            "output": {"counts": [[1, 1, 1]]},
            "defect": "Missing suffix match ('he' inside 'she') when failure links are not propagated",
        },
        {
            "name": "aho-repeated-texts-state-reset",
            "input": {"task": "aho", "patterns": ["cat"], "texts": ["cat", "cat", "dog"]},
            "output": {"counts": [[1], [1], [0]]},
            "defect": "Accumulating counts across separate texts without per-text state reset",
        },
    ]
    return tests


def run_student_tests():
    """Execute all student tests and print validation results."""
    tests = create_student_tests()
    fixtures = []
    print(f"Running {len(tests)} student tests...")
    passed = 0
    for idx, test in enumerate(tests, 1):
        task_name = test["input"]["task"]
        func = getattr(algorithms, task_name)
        actual = func(test["input"])
        is_valid = check(test["input"], actual, test["output"])
        status = "PASS" if is_valid else "FAIL"
        if is_valid:
            passed += 1
        print(f"[{status}] Test {idx:02d}: {test['name']} ({task_name})")
        if not is_valid:
            print(f"  Input:    {test['input']}")
            print(f"  Expected: {test['output']}")
            print(f"  Actual:   {actual}")

        fixtures.append({
            "name": test["name"],
            "command": task_name,
            "input": test["input"],
            "expected": test["output"],
            "actual": actual,
            "status": status,
            "defect": test["defect"],
        })

    print(f"\nStudent Tests Result: {passed}/{len(tests)} passed.\n")
    return fixtures


def run_search_benchmarks():
    """Conduct reproducible benchmarks for Naive, KMP, and RK across 3 sizes in random and repetitive cases."""
    print("Conducting Search Benchmarks (Naive vs KMP vs RK)...")

    # Three increasing sizes in common domain (n, m <= 3000)
    sizes = [
        ("Small", 500, 20),
        ("Medium", 1500, 50),
        ("Large", 3000, 100),
    ]

    benchmark_results = []
    seed = 20261108
    rng = random.Random(seed)

    # Printable ASCII alphabet subset (letters and digits)
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    for label, n, m in sizes:
        # Case 1: Random Text & Pattern
        text_rand = "".join(rng.choice(alphabet) for _ in range(n))
        # Place pattern inside text at known locations to guarantee occurrences
        pat_start = rng.randint(0, n - m)
        pattern_rand = text_rand[pat_start : pat_start + m]

        # Case 2: Repetitive / Pathological Text & Pattern
        text_rep = "a" * n
        pattern_rep = "a" * m

        cases = [
            ("Random", text_rand, pattern_rand),
            ("Repetitive", text_rep, pattern_rep),
        ]

        for case_type, text, pattern in cases:
            req = {"task": "dummy", "text": text, "pattern": pattern}

            # 1. Correctness check first: verify all three give exact same positions
            req_naive = dict(req, task="naive")
            req_kmp = dict(req, task="kmp")
            req_rk = dict(req, task="rk")

            ans_naive = algorithms.naive(req_naive)["positions"]
            ans_kmp = algorithms.kmp(req_kmp)["positions"]
            ans_rk = algorithms.rk(req_rk)["positions"]

            assert ans_naive == ans_kmp == ans_rk, (
                f"Mismatch in positions at {label} {case_type}: "
                f"Naive={len(ans_naive)}, KMP={len(ans_kmp)}, RK={len(ans_rk)}"
            )

            # Warm-up run
            for _ in range(2):
                algorithms.naive(req_naive)
                algorithms.kmp(req_kmp)
                algorithms.rk(req_rk)

            # Timed runs (at least 3 runs per algorithm)
            for alg_name, func, r in [
                ("naive", algorithms.naive, req_naive),
                ("kmp", algorithms.kmp, req_kmp),
                ("rk", algorithms.rk, req_rk),
            ]:
                times_ms = []
                for _ in range(5):  # 5 runs to get accurate median
                    t0 = time.perf_counter()
                    func(r)
                    t1 = time.perf_counter()
                    times_ms.append((t1 - t0) * 1000.0)

                # Sort to find median
                sorted_times = sorted(times_ms)
                median_ms = sorted_times[len(sorted_times) // 2]
                r1, r2, r3 = times_ms[0], times_ms[1], times_ms[2]

                benchmark_results.append({
                    "case": f"{label} ({case_type})",
                    "n": n,
                    "m": m,
                    "seed": f"seed={seed}",
                    "algorithm": alg_name,
                    "run1": round(r1, 3),
                    "run2": round(r2, 3),
                    "run3": round(r3, 3),
                    "median": round(median_ms, 3),
                    "unit": "ms",
                    "matches": len(ans_naive),
                    "correct": True,
                })
                print(
                    f"{label:6s} | {case_type:10s} | {alg_name:6s} | "
                    f"n={n}, m={m} | median={median_ms:.3f} ms | matches={len(ans_naive)}"
                )

    return benchmark_results


if __name__ == "__main__":
    fixtures = run_student_tests()
    # Save fixtures to tests/student/fixtures.json
    fixtures_file = repo_root / "tests" / "student" / "fixtures.json"
    fixtures_file.write_text(json.dumps(fixtures, indent=2), encoding="utf-8")
    print(f"Saved student fixtures to {fixtures_file}")

    benchmarks = run_search_benchmarks()
    benchmarks_file = repo_root / "tests" / "student" / "benchmarks.json"
    benchmarks_file.write_text(json.dumps(benchmarks, indent=2), encoding="utf-8")
    print(f"Saved benchmark results to {benchmarks_file}")
