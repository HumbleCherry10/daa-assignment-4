"""Assignment 4 — Dynamic Programming and String Processing.

Clean, human-readable, and robust implementations of:
1. lcs: Longest Common Subsequence with path reconstruction
2. merge: Ordered adjacent-block merging with interval DP and chronological plan
3. tree: Tree Maximum Weight Independent Set with iterative post-order DP
4. naive: Baseline exact string matching
5. kmp: Knuth-Morris-Pratt exact string matching with prefix function
6. rk: Rabin-Karp exact string matching with rolling hash (base 31, mod 101)
7. suffix: Suffix Array via prefix doubling and Kasai LCP array
8. aho: Aho-Corasick automaton with reverse-failure visit propagation
"""

from collections import deque


def lcs(request):
    """Compare two versions of a sequence while preserving the order of shared characters.
    
    dp[i][j] stores the LCS length of prefixes a[0..i-1] and b[0..j-1].
    Reconstructs one valid optimal subsequence by backtracking from (len(a), len(b)).
    """
    a = request["a"]
    b = request["b"]
    n, m = len(a), len(b)

    if n == 0 or m == 0:
        return {"length": 0, "sequence": ""}

    # dp[i][j] = length of LCS between a[:i] and b[:j]
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        char_a = a[i - 1]
        dp_i = dp[i]
        dp_prev = dp[i - 1]
        for j in range(1, m + 1):
            if char_a == b[j - 1]:
                dp_i[j] = dp_prev[j - 1] + 1
            else:
                top = dp_prev[j]
                left = dp_i[j - 1]
                dp_i[j] = top if top >= left else left

    optimal_length = dp[n][m]

    # Reconstruct subsequence by following matching characters backwards
    reconstructed = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            reconstructed.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    reconstructed.reverse()
    return {"length": optimal_length, "sequence": "".join(reconstructed)}


def merge(request):
    """Plan the cheapest sequence of adjacent block merges when the original order must be preserved.
    
    Uses interval dynamic programming. For interval [l, r], dp[l][r] is the minimum cost.
    Reconstructs a chronological valid plan where child merges precede parent merges.
    """
    sizes = request["sizes"]
    n = len(sizes)

    if n <= 1:
        return {"cost": 0, "plan": []}

    # Precompute prefix sums for O(1) interval sum queries
    pref = [0] * (n + 1)
    for i in range(n):
        pref[i + 1] = pref[i] + sizes[i]

    def interval_sum(l, r):
        return pref[r + 1] - pref[l]

    # dp[l][r] stores minimum merge cost for range [l..r]
    # split[l][r] stores optimal split point k, where intervals are [l..k] and [k+1..r]
    dp = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]

    for length in range(2, n + 1):
        for l in range(n - length + 1):
            r = l + length - 1
            best_cost = None
            best_k = l
            sum_lr = interval_sum(l, r)

            for k in range(l, r):
                candidate = dp[l][k] + dp[k + 1][r] + sum_lr
                if best_cost is None or candidate < best_cost:
                    best_cost = candidate
                    best_k = k

            dp[l][r] = best_cost
            split[l][r] = best_k

    # Reconstruct chronological plan:
    # A valid merge of [l, k] and [k+1, r] requires both sub-blocks to be formed first.
    # Therefore, recursively emit sub-plans before emitting the current [l, k, r] merge.
    plan = []

    def build_plan(l, r):
        if l >= r:
            return
        k = split[l][r]
        build_plan(l, k)
        build_plan(k + 1, r)
        plan.append([l, k, r])

    build_plan(0, n - 1)
    return {"cost": dp[0][n - 1], "plan": plan}


def tree(request):
    """Choose a maximum-value set when neighbouring vertices are incompatible and conflicts form a tree.
    
    Computes Maximum Weight Independent Set using take/skip DP.
    Avoids recursion to support deep linear chains up to n=100,000 without stack overflow.
    """
    n = request["n"]
    weights = request["weights"]
    edges = request["edges"]

    if n == 0:
        return {"weight": 0, "selected": []}

    # Build adjacency list
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    # Iterative BFS to establish tree hierarchy (parent pointers and bottom-up order)
    root = 0
    parent = [-1] * n
    bfs_order = []
    visited = [False] * n

    queue = deque([root])
    visited[root] = True

    while queue:
        curr = queue.popleft()
        bfs_order.append(curr)
        for neighbor in adj[curr]:
            if not visited[neighbor]:
                visited[neighbor] = True
                parent[neighbor] = curr
                queue.append(neighbor)

    # dp[u][0]: max weight in u's subtree if u is NOT selected (can be 0 if all choices negative)
    # dp[u][1]: max weight in u's subtree if u IS selected
    dp0 = [0] * n
    dp1 = [0] * n

    # Bottom-up evaluation in reverse BFS order
    for u in reversed(bfs_order):
        # If u is selected, we take weights[u] + sum of best non-selected values of its children
        sum_children_not_taken = 0
        sum_children_best = 0

        for neighbor in adj[u]:
            if neighbor != parent[u]:
                sum_children_not_taken += dp0[neighbor]
                # If child is not taken, its best is max(dp0, dp1)
                best_child = dp0[neighbor] if dp0[neighbor] >= dp1[neighbor] else dp1[neighbor]
                sum_children_best += best_child

        dp1[u] = weights[u] + sum_children_not_taken
        dp0[u] = sum_children_best

    # Optimal total weight at root
    # Since an empty set is valid, negative overall weights default to weight 0
    root_weight = max(dp0[root], dp1[root], 0)

    # Reconstruct selected vertices top-down iteratively
    selected = []
    if root_weight > 0:
        # State queue stores (node, must_skip)
        root_must_take = dp1[root] > dp0[root]
        reconstruct_queue = deque([(root, not root_must_take)])

        while reconstruct_queue:
            u, skip_u = reconstruct_queue.popleft()

            if not skip_u:
                # u is selected
                selected.append(u)
                # All children must be skipped
                for neighbor in adj[u]:
                    if neighbor != parent[u]:
                        reconstruct_queue.append((neighbor, True))
            else:
                # u is skipped; for each child, choose whether to take or skip based on dp values
                for neighbor in adj[u]:
                    if neighbor != parent[u]:
                        take_child = dp1[neighbor] > dp0[neighbor]
                        reconstruct_queue.append((neighbor, not take_child))

    return {"weight": root_weight, "selected": selected}


def naive(request):
    """Establish a simple exact-search baseline against which the other two searches can be checked."""
    text = request["text"]
    pattern = request["pattern"]
    n, m = len(text), len(pattern)

    # Empty pattern matches every boundary 0..n
    if m == 0:
        return {"positions": list(range(n + 1))}

    if m > n:
        return {"positions": []}

    positions = []
    limit = n - m
    for i in range(limit + 1):
        match = True
        for j in range(m):
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            positions.append(i)

    return {"positions": positions}


def kmp(request):
    """Reuse information about matched prefixes to avoid restarting the search after every mismatch."""
    text = request["text"]
    pattern = request["pattern"]
    n, m = len(text), len(pattern)

    if m == 0:
        return {"positions": list(range(n + 1))}

    if m > n:
        return {"positions": []}

    # Precompute prefix function pi for the pattern
    pi = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and pattern[i] != pattern[k]:
            k = pi[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        pi[i] = k

    # Search using prefix fallback
    positions = []
    q = 0  # Number of characters currently matched
    for i in range(n):
        while q > 0 and pattern[q] != text[i]:
            q = pi[q - 1]
        if pattern[q] == text[i]:
            q += 1
        if q == m:
            positions.append(i - m + 1)
            q = pi[m - 1]  # Fallback to preserve overlapping occurrences

    return {"positions": positions}


def rk(request):
    """Reject windows with unequal fingerprints and verify every equal-hash candidate."""
    text = request["text"]
    pattern = request["pattern"]
    n, m = len(text), len(pattern)

    if m == 0:
        return {"positions": list(range(n + 1))}

    if m > n:
        return {"positions": []}

    base = 31
    mod = 101

    # Precompute base^(m-1) % mod
    highest_power = 1
    for _ in range(m - 1):
        highest_power = (highest_power * base) % mod

    # Compute pattern hash and initial window hash
    pattern_hash = 0
    window_hash = 0
    for i in range(m):
        pattern_hash = (pattern_hash * base + ord(pattern[i])) % mod
        window_hash = (window_hash * base + ord(text[i])) % mod

    positions = []

    # Slide window across text
    for i in range(n - m + 1):
        if window_hash == pattern_hash:
            # Hash match is a candidate: verify actual characters
            match = True
            for j in range(m):
                if text[i + j] != pattern[j]:
                    match = False
                    break
            if match:
                positions.append(i)

        if i < n - m:
            # Roll hash to next window
            outgoing = ord(text[i])
            incoming = ord(text[i + m])
            window_hash = ((window_hash - outgoing * highest_power) * base + incoming) % mod
            window_hash = (window_hash % mod + mod) % mod

    return {"positions": positions}


def suffix(request):
    """Order the text suffixes and use adjacent common prefixes to find repeated substrings.
    
    Constructs suffix array using prefix doubling, computes LCP array using Kasai's algorithm,
    and identifies a longest repeated substring (with overlaps allowed).
    """
    text = request["text"]
    n = len(text)

    if n == 0:
        return {"sa": [], "lcp": [], "repeated": ""}

    if n == 1:
        return {"sa": [0], "lcp": [0], "repeated": ""}

    # Prefix doubling to compute Suffix Array
    sa = list(range(n))
    rank = [ord(c) for c in text]
    k = 1

    while k < n:
        # Sort suffixes by rank pair: (rank[i], rank[i + k] if i + k < n else -1)
        sa.sort(key=lambda i: (rank[i], rank[i + k] if i + k < n else -1))

        # Assign new ranks
        new_rank = [0] * n
        new_rank[sa[0]] = 0
        for idx in range(1, n):
            prev_i = sa[idx - 1]
            curr_i = sa[idx]
            prev_pair = (rank[prev_i], rank[prev_i + k] if prev_i + k < n else -1)
            curr_pair = (rank[curr_i], rank[curr_i + k] if curr_i + k < n else -1)

            if curr_pair == prev_pair:
                new_rank[curr_i] = new_rank[prev_i]
            else:
                new_rank[curr_i] = new_rank[prev_i] + 1

        rank = new_rank
        if rank[sa[n - 1]] == n - 1:
            # All ranks are distinct
            break
        k *= 2

    # Kasai's algorithm to compute LCP array
    # pos[i] is the position of suffix i in the suffix array sa
    pos = [0] * n
    for i in range(n):
        pos[sa[i]] = i

    lcp = [0] * n
    h = 0
    for i in range(n):
        if pos[i] > 0:
            j = sa[pos[i] - 1]
            while i + h < n and j + h < n and text[i + h] == text[j + h]:
                h += 1
            lcp[pos[i]] = h
            if h > 0:
                h -= 1
        else:
            h = 0

    # Longest repeated substring corresponds to maximum LCP value > 0
    max_lcp = 0
    best_idx = 0
    for idx in range(1, n):
        if lcp[idx] > max_lcp:
            max_lcp = lcp[idx]
            best_idx = idx

    if max_lcp > 0:
        start = sa[best_idx]
        repeated = text[start : start + max_lcp]
    else:
        repeated = ""

    return {"sa": sa, "lcp": lcp, "repeated": repeated}


def aho(request):
    """Build one dictionary automaton and count its patterns in several independent texts.
    
    Uses Aho-Corasick trie with failure links and reverse-failure visit propagation
    for linear-time frequency counting on dense texts.
    """
    patterns = request["patterns"]
    texts = request["texts"]

    num_patterns = len(patterns)
    if num_patterns == 0:
        return {"counts": [[] for _ in texts]}

    # Build Trie
    # Each node is represented as an index in nodes list
    # trie[node] is dict: char -> child_node
    trie = [{}]
    fail = [0]
    # pattern_indices[node] stores list of pattern indices ending at this node
    pattern_indices = [[]]

    for p_idx, p in enumerate(patterns):
        curr = 0
        for char in p:
            if char not in trie[curr]:
                new_node = len(trie)
                trie[curr][char] = new_node
                trie.append({})
                fail.append(0)
                pattern_indices.append([])
            curr = trie[curr][char]
        pattern_indices[curr].append(p_idx)

    # Build failure links using BFS
    queue = deque()
    # BFS order of states will give reverse topological order when traversed backwards
    bfs_order = []

    for char, child in trie[0].items():
        fail[child] = 0
        queue.append(child)

    while queue:
        curr = queue.popleft()
        bfs_order.append(curr)

        for char, child in trie[curr].items():
            f = fail[curr]
            while f > 0 and char not in trie[f]:
                f = fail[f]
            if char in trie[f]:
                fail[child] = trie[f][char]
            else:
                fail[child] = 0
            queue.append(child)

    # Query texts independently
    all_counts = []
    total_states = len(trie)

    for text in texts:
        row_counts = [0] * num_patterns
        if len(text) == 0:
            all_counts.append(row_counts)
            continue

        # Step 1: Traverse automaton and record direct visits to each state
        visits = [0] * total_states
        curr = 0
        for char in text:
            while curr > 0 and char not in trie[curr]:
                curr = fail[curr]
            if char in trie[curr]:
                curr = trie[curr][char]
            else:
                curr = 0
            visits[curr] += 1

        # Step 2: Propagate visits in reverse BFS order along failure links
        for st in reversed(bfs_order):
            visits[fail[st]] += visits[st]

        # Step 3: Aggregate counts for all patterns matching at each state
        for st in range(total_states):
            count = visits[st]
            if count > 0:
                for p_idx in pattern_indices[st]:
                    row_counts[p_idx] = count

        all_counts.append(row_counts)

    return {"counts": all_counts}
