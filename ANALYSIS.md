# Assignment 4 — Analysis (Complete in English)

**Course:** Design and Analysis of Algorithms  
**Topic:** Dynamic Programming and String Processing  
**Implementation Language:** Python 3 (Python 3.14.3, 64-bit)  
**Author Environment:** Windows 11 Pro 64-bit, 13th Gen Intel(R) Core(TM) i5-13500H, 16 GB RAM  

---

## 1. Environment and Commands

### Runtime and Toolchain
- **Language / Runtime:** Python 3.14.3 (CPython 64-bit)
- **Host OS:** Microsoft Windows 11 Pro (Build 22631 / 64-bit)
- **CPU:** 13th Gen Intel(R) Core(TM) i5-13500H (12 physical cores, 16 logical processors)
- **Memory:** 16 GB RAM (16,481,336 KB visible physical memory)

### Build, Run, and Verification Commands
All commands run from the repository root:

```powershell
# 1. Verify environment and protocol transport
python tools/run.py --setup

# 2. Run official public check suite (44 test cases + double-batch state reset)
python tools/run.py --check

# 3. Run the comprehensive student test suite (32 tests across all 8 tasks)
python tools/student_test_and_benchmark.py

# 4. Stream student JSON-lines fixture through the active runner
python tools/run.py --input tests/student/student_tests.jsonl
```

---

## 2. Algorithm Explanations

### Part 1: Longest Common Subsequence (`lcs`)

- **State / Invariant:**
  Let $a$ and $b$ be the two input strings of lengths $n$ and $m$. We define a 2D table `dp[i][j]` for $0 \le i \le n$ and $0 \le j \le m$, representing the length of the longest common subsequence between prefix $a[0..i-1]$ and prefix $b[0..j-1]$.
  - Index $i$ represents the number of characters considered from string $a$.
  - Index $j$ represents the number of characters considered from string $b$.

- **Transitions and Base Cases:**
  - Base cases: `dp[i][0] = 0` for all $0 \le i \le n$ and `dp[0][j] = 0` for all $0 \le j \le m$, since any comparison against an empty prefix yields an empty LCS.
  - Transition for $i, j \ge 1$:
    $$\text{dp}[i][j] = \begin{cases} \text{dp}[i-1][j-1] + 1 & \text{if } a[i-1] == b[j-1] \\ \max(\text{dp}[i-1][j], \text{dp}[i][j-1]) & \text{if } a[i-1] \ne b[j-1] \end{cases}$$

- **Processing Order:**
  Row-major order (outer loop $i = 1 \dots n$, inner loop $j = 1 \dots m$). When computing `dp[i][j]`, its dependencies `dp[i-1][j-1]`, `dp[i-1][j]`, and `dp[i][j-1]` are strictly already computed and finalized in memory.

- **Correctness Argument:**
  By the optimal substructure of LCS:
  - If $a[i-1] == b[j-1]$, this character can safely be paired as the last element of an optimal subsequence of $a[0..i-1]$ and $b[0..j-1]$, giving length $\text{dp}[i-1][j-1] + 1$.
  - If $a[i-1] \ne b[j-1]$, the two characters cannot be paired together. At least one of them cannot belong to the common subsequence. Therefore, the optimal LCS length is bounded by $\max(\text{dp}[i-1][j], \text{dp}[i][j-1])$.

- **Reconstruction and Tie Handling:**
  Reconstruction starts at $(n, m)$ and walks backwards to $(0, 0)$:
  - If $a[i-1] == b[j-1]$, character $a[i-1]$ was matched: append it to the reconstruction list and step diagonally to $(i-1, j-1)$.
  - Else if $\text{dp}[i-1][j] \ge \text{dp}[i][j-1]$, step upwards to $(i-1, j)$.
  - Else step leftwards to $(i, j-1)$.
  When $\text{dp}[i-1][j] == \text{dp}[i][j-1]$, both branches lead to an optimal subsequence of the same maximal length. Choosing $\text{dp}[i-1][j] \ge \text{dp}[i][j-1]$ consistently resolves ties while preserving validity. Reversing the collected list restores chronological order.

- **Time and Memory Complexity:**
  - Time: $\mathcal{O}((n + 1)(m + 1))$ operations to fill the table plus $\mathcal{O}(n + m)$ operations to backtrack, satisfying $\mathcal{O}(|a| \cdot |b|)$.
  - Auxiliary Memory: $\mathcal{O}((n + 1)(m + 1))$ integers using Python's native list-of-lists. For $n, m \le 1000$, the table contains $\le 10^6$ entries ($\approx 8$ MB), which executes in $\approx 0.1$s and stays well within the 768 MiB memory limit.

- **Boundary / Defect Case:**
  `lcs-interleaved-subsequence`: $a = \text{"XAYBZCD"}$, $b = \text{"1A2B3C4D5"}$.
  - Expected: `length = 4, sequence = "ABCD"`.
  - Defect detected: Algorithms that mistakenly search for contiguous substrings rather than subsequences, or reset index pointers on non-matching characters.

---

### Part 2: Ordered Adjacent-Block Merging (`merge`)

- **State / Invariant:**
  Given array `sizes` of length $n$. For $0 \le l \le r < n$, `dp[l][r]` stores the minimum total cost required to merge the adjacent blocks from original index $l$ through $r$ into a single composite block $[l, r]$. `split[l][r]` records the split point $k$ ($l \le k < r$) that achieves this minimal cost.

- **Transitions and Base Cases:**
  - Base cases: `dp[i][i] = 0` for all $0 \le i < n$ (a single original block is already formed and requires 0 merge operations).
  - Transition for interval length $\text{len} = 2 \dots n$:
    $$\text{dp}[l][r] = \min_{l \le k < r} \Big( \text{dp}[l][k] + \text{dp}[k+1][r] \Big) + \sum_{i=l}^r sizes[i]$$
    Prefix sums `pref[i]` are precomputed in $\mathcal{O}(n)$ so that the range sum $\sum_{i=l}^r sizes[i] = pref[r+1] - pref[l]$ is answered in $\mathcal{O}(1)$.

- **Processing Order:**
  Length-increasing order: length $\text{len} = 2, 3, \dots, n$, with left boundary $l = 0 \dots n - \text{len}$ and right boundary $r = l + \text{len} - 1$. Since $k - l + 1 < \text{len}$ and $r - (k + 1) + 1 < \text{len}$, both sub-intervals $[l, k]$ and $[k+1, r]$ have strictly smaller lengths and are already finalized in `dp`.

- **Correctness Argument:**
  Preserving the initial block order requires that any composite block is a contiguous range of original indices. The very last merge that forms block $[l, r]$ must combine two contiguous sub-blocks: $[l, k]$ and $[k+1, r]$ for some $l \le k < r$. The cost paid for this final merge is always the total size of all elements in $[l, r]$, regardless of $k$. By optimal substructure, the total cost is minimized by picking the partition $k$ that minimizes the sum of costs for forming $[l, k]$ and $[k+1, r]$.

- **Chronological Plan Reconstruction:**
  To satisfy the contract that merges are valid chronologically (each merge combines two currently existing adjacent blocks in the active blocks list), child merges must occur **before** their parent merge. A recursive post-order traversal function `build_plan(l, r)`:
  1. If $l \ge r$, return.
  2. Let $k = split[l][r]$.
  3. Call `build_plan(l, k)` (merges sub-blocks within the left child).
  4. Call `build_plan(k + 1, r)` (merges sub-blocks within the right child).
  5. Append `[l, k, r]` to the global plan.
  This generates exactly $n - 1$ operations in valid chronological order.

- **Time and Memory Complexity:**
  - Time: $\sum_{\text{len}=2}^n (n - \text{len} + 1)(\text{len} - 1) = \mathcal{O}(n^3)$. For $n \le 200$, $\approx 200^3 / 6 \approx 1.33 \times 10^6$ operations, executing in $< 0.1$s in Python.
  - Auxiliary Memory: $\mathcal{O}(n^2)$ for the $n \times n$ tables `dp` and `split`.
  - Integer Precision: Python provides arbitrary-precision integers out-of-the-box, ensuring exact arithmetic even when cumulative costs exceed $2^{63}-1$.

- **Boundary / Defect Case:**
  `merge-adjacent-vs-arbitrary`: `sizes = [10, 100, 10]`.
  - Expected: `cost = 230, plan = [[0, 0, 1], [0, 1, 2]]` (or `[[1, 1, 2], [0, 0, 2]]`).
  - Defect detected: Huffman/greedy priority-queue implementations that merge non-adjacent minimum elements (10 + 10 = 20) instead of maintaining spatial adjacency.

---

### Part 3: Tree Maximum Weight Independent Set (`tree`)

- **State / Invariant:**
  Rooting the undirected tree arbitrarily at vertex 0:
  - `dp[u][1]` represents the maximum weight independent set in the subtree rooted at $u$ given that vertex $u$ **is selected**.
  - `dp[u][0]` represents the maximum weight independent set in the subtree rooted at $u$ given that vertex $u$ **is not selected**.

- **Transitions and Base Cases:**
  - For each child $v$ of $u$:
    $$\text{dp}[u][1] = weights[u] + \sum_{v \in children(u)} \text{dp}[v][0]$$
    $$\text{dp}[u][0] = \sum_{v \in children(u)} \max(\text{dp}[v][0], \text{dp}[v][1])$$
  - Base cases (leaves): `dp[w][0] = 0` and `dp[w][1] = weights[w]`.
  - Handling negative weights: An empty independent set has weight 0. Thus, overall tree optimum is $\max(\text{dp}[root][0], \text{dp}[root][1], 0)$.

- **Processing Order and Deep Chain Safety:**
  To prevent recursion stack overflow on deep linear chains ($n \le 100,000$):
  1. An iterative BFS from root 0 populates parent pointers and records the BFS visitation sequence.
  2. Bottom-up DP evaluation iterates through the BFS sequence in **reverse order** (leaves up to root). This ensures every child's DP values are fully computed before its parent is visited.
  3. Reconstruction is performed iteratively using a queue (`reconstruct_queue`).

- **Correctness Argument:**
  In any independent set, two adjacent vertices cannot both be selected:
  - If $u$ is selected, no child $v$ can be selected, forcing the child subtree to take $\text{dp}[v][0]$.
  - If $u$ is not selected, each child $v$ can independently choose whether to be selected or skipped, yielding $\max(\text{dp}[v][0], \text{dp}[v][1])$.
  Because an undirected tree has a unique simple path between any pair of vertices, choosing vertex 0 as root does not alter the graph structure or the global maximum weight.

- **Reconstruction:**
  If $\max(\text{dp}[root][0], \text{dp}[root][1], 0) == 0$, the optimal choice is the empty set (`selected = []`).
  Otherwise, we begin at the root: if $\text{dp}[root][1] > \text{dp}[root][0]$, root is selected. We push `(root, is_skipped)` onto an iterative queue:
  - If $u$ is selected: add $u$ to `selected` and push all children with `skip = True`.
  - If $u$ is skipped: for each child $v$, push $v$ with `skip = (dp[v][1] <= dp[v][0])`.

- **Time and Memory Complexity:**
  - Time: $\mathcal{O}(n)$ — each vertex and edge is traversed a constant number of times during BFS, reverse DP, and iterative reconstruction.
  - Auxiliary Memory: $\mathcal{O}(n)$ — adjacency list of $2(n-1)$ entries, flat integer arrays for `parent`, `dp0`, `dp1`, and iterative queues.

- **Boundary / Defect Case:**
  `tree-all-negative`: $n = 3$, `weights = [-5, -10, -2]`, `edges = [[0, 1], [1, 2]]`.
  - Expected: `weight = 0, selected = []`.
  - Defect detected: Implementations that force at least one vertex to be selected, returning negative weight instead of the empty set.

---

### Part 4: Exact Search Trio (`naive`, `kmp`, `rk`)

All three string search algorithms implement the exact same matching contract:
- Input: `text`, `pattern`.
- Output: `positions` — 0-based start indices in strictly increasing order.
- Overlapping occurrences must be reported.
- An empty pattern ($m = 0$) matches all $n + 1$ boundary positions: `[0, 1, ..., n]`.
- A pattern longer than text ($m > n$) returns `[]`.

#### 1. Naive Baseline (`naive`)
- **Invariant:** Test every valid start index $i \in [0, n - m]$. Candidate $i$ is recorded iff $\forall j \in [0, m-1], text[i + j] == pattern[j]$.
- **Processing Order:** Outer loop $i = 0 \dots n - m$, inner loop $j = 0 \dots m - 1$ with early exit upon first mismatched character.
- **Correctness:** Full exhaustive comparison guarantees zero false positives and zero false negatives.
- **Complexity:** Time $\mathcal{O}((n - m + 1) \cdot m + z) = \mathcal{O}(n \cdot m)$ worst case. Memory $\mathcal{O}(1)$ auxiliary beyond output list.
- **Boundary / Defect Case:** `search-overlapping`: $text = \text{"AAAA"}$, $pattern = \text{"AA"}$. Expected `[0, 1, 2]`. Detects flawed logic that advances $i$ by $m$ instead of 1.

#### 2. Knuth-Morris-Pratt (`kmp`)
- **Invariant:** Precomputes prefix function $\pi[0..m-1]$, where $\pi[i]$ is the length of the longest proper prefix of $pattern[0..i]$ that is also a suffix of $pattern[0..i]$. In the text search, state $q \in [0, m]$ tracks the length of the longest pattern prefix matching the current suffix of $text[0..i]$.
- **Transitions:**
  - When $text[i] == pattern[q]$, advance state $q \leftarrow q + 1$.
  - When a mismatch occurs ($text[i] \ne pattern[q]$), fall back to $q \leftarrow \pi[q - 1]$ repeatedly until a match is found or $q = 0$.
  - Upon full match ($q == m$), emit start index $i - m + 1$ and fall back to $q \leftarrow \pi[m - 1]$ to detect overlapping occurrences.
- **Processing Order:** Single linear pass over pattern to construct $\pi$, followed by a single linear pass over text without ever decrementing the text index $i$.
- **Correctness:** The prefix function guarantees that after matching $q$ characters, the next longest potential match that aligns with the characters seen so far has length $\pi[q-1]$. No potential match is ever skipped.
- **Complexity:** Preprocessing $\mathcal{O}(m)$, search $\mathcal{O}(n)$, output $\mathcal{O}(z)$. Total time $\mathcal{O}(n + m + z)$ deterministic. Auxiliary memory $\mathcal{O}(m)$ for array $\pi$.

#### 3. Rabin-Karp (`rk`)
- **Invariant:** Uses a polynomial rolling hash with fixed base $b = 31$, prime modulus $M = 101$, and standard ASCII character codes:
  $$H(s) = \left( \sum_{j=0}^{m-1} \text{ord}(s[j]) \cdot 31^{m-1-j} \right) \bmod 101$$
  Highest power corresponds to the leftmost character.
- **Rolling Update:**
  $$H_{i+1} = \Big( (H_i - \text{ord}(text[i]) \cdot 31^{m-1}) \cdot 31 + \text{ord}(text[i+m]) \Big) \bmod 101$$
  Negative remainders are normalized via `(H % 101 + 101) % 101`.
- **Character Verification:** Hash equality ($window\_hash == pattern\_hash$) indicates a candidate window only. Character-by-character comparison verifies true equality before reporting.
- **Candidate-Sensitive Bound:**
  - Let $c$ be the number of candidate windows having matching hash values.
  - Total running time is $\mathcal{O}(n + m + c \cdot m)$.
  - In the best case (few collisions), $c \approx z$, giving linear time $\mathcal{O}(n + m)$.
  - Because modulus 101 is intentionally tiny, on adversarial or repetitive inputs (e.g. `"a"*n` with `"a"*m`), every window collides ($c = n - m + 1$), resulting in worst-case quadratic time $\mathcal{O}(n \cdot m)$.
- **Boundary / Defect Case:** `rk-hash-collision-verification`: $text = \text{"abdj"}$, $pattern = \text{"ab"}$. Both `"ab"` and `"dj"` produce identical hash $(97 \cdot 31 + 98) \bmod 101 = 75$ and $(100 \cdot 31 + 106) \bmod 101 = 75$. Detects implementations that omit character verification and return false positive index 2.

---

### Part 5: Suffix Array and Kasai LCP (`suffix`)

- **State / Invariant:**
  - `sa`: Permutation of $0 \dots n-1$ such that suffix $text[sa[0]..n-1] < text[sa[1]..n-1] < \dots < text[sa[n-1]..n-1]$ in lexicographical order.
  - `lcp`: Array of length $n$ where `lcp[0] = 0` and `lcp[i]` is the length of the Longest Common Prefix between suffix $sa[i-1]$ and suffix $sa[i]$.
  - `repeated`: Longest substring occurring at $\ge 2$ distinct start positions.

#### Suffix Array via Prefix Doubling
- **Algorithm:**
  Initialize ranks with character ASCII values `rank[i] = ord(text[i])`. In each iteration $k = 1, 2, 4, \dots$:
  - Suffixes are ordered by a 2-tuple key: $(rank[i], rank[i + k] \text{ if } i + k < n \text{ else } -1)$.
  - Suffixes with identical 2-tuples receive identical new ranks; otherwise rank increments.
  - The process terminates when $k \ge n$ or when all $n$ ranks are distinct ($rank[sa[n-1]] == n - 1$).
- **Correctness:** By induction, if ranks reflect lexicographical order of prefixes of length $2^{k-1}$, then comparing $(rank[i], rank[i + 2^{k-1}])$ accurately compares prefixes of length $2^k$.
- **Complexity:** $\mathcal{O}(\log n)$ doubling rounds; each round sorts $n$ tuples using Python's Timsort in $\mathcal{O}(n \log n)$ time. Total time $\mathcal{O}(n \log^2 n)$, auxiliary space $\mathcal{O}(n)$.

#### Kasai's LCP Algorithm
- **Algorithm:**
  1. Invert `sa` to form position array `pos` where $pos[sa[i]] = i$.
  2. Maintain a running match counter $h = 0$.
  3. Iterate $i = 0 \dots n - 1$ in original text order:
     - If $pos[i] > 0$, look at predecessor suffix $j = sa[pos[i] - 1]$.
     - Extend $h$ while $i + h < n$ and $j + h < n$ and $text[i + h] == text[j + h]$.
     - Store $lcp[pos[i]] = h$.
     - When advancing to $i + 1$, decrement $h \leftarrow \max(0, h - 1)$.
- **Correctness:** Deleting the first character from suffix $i$ and its predecessor suffix $j$ leaves common prefixes of length at least $h - 1$. In the suffix array, suffix $j + 1$ appears before suffix $i + 1$, guaranteeing that the LCP between suffix $i + 1$ and its immediate predecessor in `sa` is at least $h - 1$. Thus, $h$ decreases at most $n$ times and increases at most $2n$ times.
- **Complexity:** Strict linear time $\mathcal{O}(n)$, auxiliary memory $\mathcal{O}(n)$.

#### Longest Repeated Substring
- **Deduction:** Any substring appearing at $\ge 2$ distinct starts must be a prefix of two different suffixes. In the sorted suffix array, the maximum common prefix between any pair of suffixes is achieved by adjacent suffixes in `sa`. Therefore, the length of the longest repeated substring is $\max_{1 \le i < n} lcp[i]$. If $\max(lcp) > 0$, slice $text[sa[best\_idx] : sa[best\_idx] + \max(lcp)]$; otherwise return `""`.

- **Boundary / Defect Case:**
  `suffix-all-identical`: $text = \text{"aaaa"}$.
  - Expected: `sa = [3, 2, 1, 0]`, `lcp = [0, 1, 2, 3]`, `repeated = "aaa"`.
  - Defect detected: Failure to support overlapping repeats (detecting only `"aa"` instead of `"aaa"`).

---

### Part 6: Aho–Corasick Multi-Pattern Search (`aho`)

- **State / Invariant:**
  - Trie automaton where each state represents a unique prefix among the dictionary patterns.
  - `fail[u]` links state $u$ to the state representing the longest proper suffix of the path to $u$ that exists in the trie.
  - `pattern_indices[u]` stores the original dictionary indices of all patterns terminating at state $u$.

- **Trie Construction & Failure Links:**
  1. Insert patterns into the trie. Duplicate pattern strings share the same terminal trie state; their separate original indices are preserved in `pattern_indices[u]`.
  2. BFS from root: states at depth 1 have `fail = 0`. For state $u$ and child $v$ on char $c$, follow failure links $f = fail[u]$ until $c$ exists or $f = 0$, setting $fail[v] = trie[f][c]$. Record BFS visitation order.

- **Reverse-Failure Visit Propagation:**
  For each text:
  1. Allocate clean visit counts `visits = [0] * total_states`.
  2. Step through the text linearly. For each character, follow trie transitions and failure links to transition state $curr$, and increment `visits[curr] += 1`.
  3. Traverse states in **reverse BFS order** (leaves/deepest nodes to root) and propagate:
     $$visits[fail[st]] += visits[st]$$
  4. For each state $st$, assign $row\_counts[p\_idx] = visits[st]$ for each $p\_idx \in pattern\_indices[st]$.

- **Correctness and Independent Texts:**
  A pattern occurrence ending at text position $i$ represents a prefix of that pattern that matches a suffix of $text[0..i]$. The reverse BFS traversal represents a reverse topological sort of the failure tree: visits to any node $u$ automatically accumulate into all ancestor suffix states along its failure path. This guarantees complete counts including nested suffixes and overlapping matches in linear time $\mathcal{O}(|text| + S)$, completely avoiding exponential output-link traversals on dense texts. State counts are re-initialized to zero for each text, guaranteeing zero cross-contamination.

- **Time and Memory Complexity:**
  - Construction: $\mathcal{O}(L + |\Sigma| \cdot S)$ time and space, where $L$ is total pattern length and $S$ is number of states.
  - Search per text: $\mathcal{O}(|text| + S)$ time.
  - Output: $\mathcal{O}(q \cdot p)$ where $q$ is number of texts and $p$ is number of patterns.

- **Boundary / Defect Case:**
  `aho-nested-suffix-patterns`: $patterns = [\text{"she"}, \text{"he"}, \text{"hers"}]$, $texts = [\text{"ushers"}]$.
  - Expected: `counts = [[1, 1, 1]]`.
  - Defect detected: Missing `"he"` inside `"she"` at index 3 when suffix failure links are not propagated.

---

## 3. Own Tests

The 32 curated student test cases located in `tests/student/fixtures.json` and `tests/student/student_tests.jsonl` were executed against our implementation and verified with `public_validate.check`.

| Command | Fixture Name / Path | Expected Result | Actual Result / Log | What it Checks |
|---|---|---|---|---|
| `lcs` | `lcs-both-empty` | `{"length": 0, "sequence": ""}` | `{"length": 0, "sequence": ""}` [PASS] | Both strings empty base case |
| `lcs` | `lcs-one-empty` | `{"length": 0, "sequence": ""}` | `{"length": 0, "sequence": ""}` [PASS] | One empty string, bounds validation |
| `lcs` | `lcs-interleaved-subsequence` | `{"length": 4, "sequence": "ABCD"}` | `{"length": 4, "sequence": "ABCD"}` [PASS] | Non-contiguous characters (subsequence vs substring) |
| `lcs` | `lcs-repeated-characters` | `{"length": 2, "sequence": "AA"}` | `{"length": 2, "sequence": "AA"}` [PASS] | Duplicate character handling without overcounting |
| `lcs` | `lcs-alternative-optimal` | `{"length": 1, "sequence": "A"}` | `{"length": 1, "sequence": "A"}` [PASS] | Alternative optimal witness ("A" or "B") |
| `merge` | `merge-empty` | `{"cost": 0, "plan": []}` | `{"cost": 0, "plan": []}` [PASS] | 0 blocks returns cost 0 and empty plan |
| `merge` | `merge-single-block` | `{"cost": 0, "plan": []}` | `{"cost": 0, "plan": []}` [PASS] | 1 block requires 0 merges |
| `merge` | `merge-with-zeros` | `{"cost": 20, "plan": [...]}` | `{"cost": 20, "plan": [...]}` [PASS] | Interval DP with zero-weighted blocks |
| `merge` | `merge-adjacent-vs-arbitrary` | `{"cost": 230, "plan": [...]}` | `{"cost": 230, "plan": [...]}` [PASS] | Enforces contiguous adjacency vs arbitrary greedy |
| `merge` | `merge-large-costs-64bit` | `{"cost": 5000000000, "plan": [...]}` | `{"cost": 5000000000, "plan": [...]}` [PASS] | Signed 64-bit integer cost overflow protection |
| `tree` | `tree-empty` | `{"weight": 0, "selected": []}` | `{"weight": 0, "selected": []}` [PASS] | Empty tree ($n=0$) base case |
| `tree` | `tree-single-negative` | `{"weight": 0, "selected": []}` | `{"weight": 0, "selected": []}` [PASS] | Single negative vertex defaults to empty set |
| `tree` | `tree-all-negative` | `{"weight": 0, "selected": []}` | `{"weight": 0, "selected": []}` [PASS] | All-negative tree vertices default to weight 0 |
| `tree` | `tree-deep-chain` | `{"weight": 30, "selected": [0, 2, 4]}` | `{"weight": 30, "selected": [0, 2, 4]}` [PASS] | Deep linear chain non-adjacency and recursion safety |
| `tree` | `tree-star-center-vs-leaves` | `{"weight": 20, "selected": [1, 2, 3, 4]}` | `{"weight": 20, "selected": [1, 2, 3, 4]}` [PASS] | Star graph: sum of leaves (20) beats center (15) |
| `naive` | `search-empty-pattern` | `{"positions": [0, 1, 2, 3, 4, 5]}` | `{"positions": [0, 1, 2, 3, 4, 5]}` [PASS] | Empty pattern returns all $n+1$ boundary positions |
| `kmp` | `search-pattern-longer` | `{"positions": []}` | `{"positions": []}` [PASS] | Pattern longer than text returns empty array |
| `kmp` | `search-overlapping` | `{"positions": [0, 1, 2]}` | `{"positions": [0, 1, 2]}` [PASS] | Preserves overlapping match starts |
| `naive` | `search-case-and-punctuation` | `{"positions": [0, 12]}` | `{"positions": [0, 12]}` [PASS] | ASCII exact matching with punctuation & case |
| `rk` | `rk-hash-collision-verification` | `{"positions": [0]}` | `{"positions": [0]}` [PASS] | Verifies candidates to reject hash collision ("dj" vs "ab") |
| `rk` | `rk-negative-modulo-normalization`| `{"positions": [2]}` | `{"positions": [2]}` [PASS] | Proper positive normalization of rolling remainder |
| `suffix` | `suffix-empty` | `{"sa": [], "lcp": [], "repeated": ""}` | `{"sa": [], "lcp": [], "repeated": ""}` [PASS] | Empty text returns empty arrays and empty repeated |
| `suffix` | `suffix-single-char` | `{"sa": [0], "lcp": [0], "repeated": ""}` | `{"sa": [0], "lcp": [0], "repeated": ""}` [PASS] | Single character has no repeat |
| `suffix` | `suffix-all-identical` | `{"sa": [3, 2, 1, 0], "repeated": "aaa"}` | `{"sa": [3, 2, 1, 0], "repeated": "aaa"}` [PASS] | Suffix array ordering and overlapping longest repeat |
| `suffix` | `suffix-all-distinct` | `{"sa": [0, 1, 2, 3, 4, 5], "repeated": ""}` | `{"sa": [0, 1, 2, 3, 4, 5], "repeated": ""}` [PASS] | All distinct characters yield no repeated substring |
| `suffix` | `suffix-tie-longest-repeats` | `{"sa": [...], "repeated": "_abc"}` | `{"sa": [...], "repeated": "_abc"}` [PASS] | Multiple tied maximal repeats of length 4 |
| `aho` | `aho-empty-dictionary` | `{"counts": [[], []]}` | `{"counts": [[], []]}` [PASS] | Empty pattern dictionary returns empty count row |
| `aho` | `aho-empty-texts` | `{"counts": []}` | `{"counts": []}` [PASS] | Empty texts array returns empty list |
| `aho` | `aho-empty-text-string` | `{"counts": [[0, 0], [1, 0]]}` | `{"counts": [[0, 0], [1, 0]]}` [PASS] | Empty text string returns row of zeros |
| `aho` | `aho-duplicate-patterns` | `{"counts": [[2, 2]]}` | `{"counts": [[2, 2]]}` [PASS] | Duplicate dictionary entries each receive full counts |
| `aho` | `aho-nested-suffix-patterns` | `{"counts": [[1, 1, 1]]}` | `{"counts": [[1, 1, 1]]}` [PASS] | Matches nested suffix patterns ("he" inside "she") |
| `aho` | `aho-repeated-texts-state-reset` | `{"counts": [[1], [1], [0]]}` | `{"counts": [[1], [1], [0]]}` [PASS] | Guarantees clean state reset across independent texts |

---

## 4. Search Comparison

### Experimental Methodology
- **Common Domain:** Tested across three increasing input sizes satisfying $n, m \le 3000$.
- **Inputs Tested:** Identical text and pattern inputs provided to `naive`, `kmp`, and `rk`.
  - **Random Case:** Alphanumeric ASCII characters generated using Python's pseudo-random generator with fixed seed `20261108`. The pattern is guaranteed to appear in the text.
  - **Repetitive Case:** Pathological all-`'a'` sequences ($text = \text{"a"}^n$, $pattern = \text{"a"}^m$), creating dense overlapping matches.
- **Correctness Verification:** Prior to timing measurements, the output lists of all three algorithms were asserted to be strictly identical (`ans_naive == ans_kmp == ans_rk`).
- **Timing Protocol:**
  - 2 unmeasured warm-up iterations executed first.
  - 5 measured runs executed using `time.perf_counter()`.
  - Timing boundary isolates algorithm execution only (excluding compilation and JSON parsing).
  - Raw times for first 3 runs, median across all runs, and time unit (milliseconds, `ms`) are recorded below.

### Empirical Results Table

| Case | $n$ | $m$ | Seed / Generator | Algorithm | Run 1 (ms) | Run 2 (ms) | Run 3 (ms) | Median (ms) | Correct Outputs Checked |
|---|---:|---:|---|---|---:|---:|---:|---:|---|
| Small (Random) | 500 | 20 | seed=20261108 | naive | 0.085 | 0.088 | 0.086 | **0.086** | Verified (1 match) |
| Small (Random) | 500 | 20 | seed=20261108 | kmp | 0.052 | 0.046 | 0.045 | **0.045** | Verified (1 match) |
| Small (Random) | 500 | 20 | seed=20261108 | rk | 0.145 | 0.142 | 0.143 | **0.143** | Verified (1 match) |
| Small (Repetitive) | 500 | 20 | seed=20261108 | naive | 0.565 | 0.558 | 0.562 | **0.565** | Verified (481 matches) |
| Small (Repetitive) | 500 | 20 | seed=20261108 | kmp | 0.108 | 0.103 | 0.102 | **0.102** | Verified (481 matches) |
| Small (Repetitive) | 500 | 20 | seed=20261108 | rk | 0.767 | 0.773 | 0.769 | **0.767** | Verified (481 matches) |
| Medium (Random) | 1500 | 50 | seed=20261108 | naive | 0.291 | 0.245 | 0.261 | **0.261** | Verified (1 match) |
| Medium (Random) | 1500 | 50 | seed=20261108 | kmp | 0.135 | 0.131 | 0.131 | **0.131** | Verified (1 match) |
| Medium (Random) | 1500 | 50 | seed=20261108 | rk | 0.434 | 0.422 | 0.443 | **0.422** | Verified (1 match) |
| Medium (Repetitive) | 1500 | 50 | seed=20261108 | naive | 4.628 | 4.072 | 4.471 | **4.382** | Verified (1451 matches) |
| Medium (Repetitive) | 1500 | 50 | seed=20261108 | kmp | 0.288 | 0.292 | 0.288 | **0.292** | Verified (1451 matches) |
| Medium (Repetitive) | 1500 | 50 | seed=20261108 | rk | 4.827 | 4.786 | 4.980 | **4.786** | Verified (1451 matches) |
| Large (Random) | 3000 | 100 | seed=20261108 | naive | 0.486 | 0.499 | 0.523 | **0.505** | Verified (1 match) |
| Large (Random) | 3000 | 100 | seed=20261108 | kmp | 0.265 | 0.270 | 0.277 | **0.270** | Verified (1 match) |
| Large (Random) | 3000 | 100 | seed=20261108 | rk | 0.813 | 0.808 | 1.016 | **1.016** | Verified (1 match) |
| Large (Repetitive) | 3000 | 100 | seed=20261108 | naive | 15.966 | 17.453 | 16.972 | **15.966** | Verified (2901 matches) |
| Large (Repetitive) | 3000 | 100 | seed=20261108 | kmp | 0.553 | 0.537 | 0.542 | **0.537** | Verified (2901 matches) |
| Large (Repetitive) | 3000 | 100 | seed=20261108 | rk | 15.418 | 16.470 | 14.703 | **16.131** | Verified (2901 matches) |

### Algorithmic Observations & Discussion

1. **Random Text Performance:**
   - On uniformly distributed random characters, Naive search runs remarkably fast (0.505 ms at $n=3000$) because almost every comparison mismatches on the 1st or 2nd character. The expected number of character comparisons per window is $\approx \frac{1}{1 - 1/|\Sigma|} = \mathcal{O}(1)$.
   - KMP outperforms Naive even on random text (0.270 ms vs. 0.505 ms) due to optimal state tracking and Python's tight loop.
   - Rabin-Karp incurs slight arithmetic overhead (1.016 ms) because updating the polynomial rolling hash on every window takes more arithmetic operations than a single character inequality check.

2. **Repetitive Text Performance (Pathological Worst Case):**
   - On repetitive text ($text = \text{"a"}^{3000}$, $pattern = \text{"a"}^{100}$), Naive search degrades sharply to $\mathcal{O}((n - m + 1) \cdot m)$, taking **15.966 ms** for 2,901 matches.
   - KMP demonstrates its theoretical guarantee: running time scales strictly linearly ($\mathcal{O}(n + m)$), taking only **0.537 ms**—**over 30 times faster than Naive search**.
   - Rabin-Karp takes **16.131 ms**, exhibiting quadratic behavior virtually identical to Naive search. Every single window of 100 `'a'` characters produces the exact same hash value:
     $$H(\text{"a"}^{100}) = \sum_{j=0}^{99} 97 \cdot 31^j \pmod{101}$$
     Because the hash matches on every window, Rabin-Karp triggers the character verification branch for all 2,901 windows, confirming the theoretical candidate-sensitive bound $\mathcal{O}(n + m + c \cdot m)$ with $c = 2901$.

3. **Role of Deliberately Small Modulus in Rabin-Karp:**
   - The choice of modulus $M = 101$ in Assignment 4 is an educational laboratory designed to force and expose hash collisions. With only 101 possible hash buckets, the Pigeonhole Principle guarantees that even modest alphabets produce frequent hash collisions (such as `"ab"` and `"dj"` both hashing to 75).
   - In real-world production systems, rolling hashes utilize large 64-bit Mersenne primes (e.g., $2^{61}-1$) or randomized bases, reducing the probability of accidental collisions to $< 10^{-18}$. However, the requirement for character verification remains mathematically essential for exact search correctness regardless of modulus size.

---

## 5. Sources and AI Assistance

- **Course Materials:**
  - Week 8 Lecture Notes: Dynamic Programming patterns (prefix LCS, interval partition merge, tree take/skip MWIS).
  - Week 9 Lecture Notes: Knuth-Morris-Pratt prefix function, Rabin-Karp polynomial rolling hash with collision verification.
  - Week 10 Lecture Notes: Suffix Array prefix doubling, Kasai LCP linear algorithm, Aho-Corasick trie and failure automaton.
  - Course specification documents: `Assignment_4_EN.md`, `CONTRACTS.md`, `RUBRIC.md`, `TESTING.md`, `LECTURE_CLARIFICATIONS_EN_RU.md`.

- **AI Assistance & Verification:**
  - AI assistance was used as a pair-programming partner to help design the implementation structure in `Python/source/algorithms.py`, structure student test edge cases, and format empirical benchmark tables.
  - **Independent Verification:** All algorithm code, mathematical invariants, transitions, and edge cases were independently verified and reviewed. Correctness was rigorously confirmed by passing all 44 official public checks, the double-batch state reset check, and 32 custom student tests without errors.
