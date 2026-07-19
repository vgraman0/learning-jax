# Einsum Examples

`np.einsum` expresses tensor contractions in **Einstein summation notation**: you label every axis of every operand with a letter, then declare which labels survive into the output. Everything else follows from three rules.

| Rule | Meaning |
| --- | --- |
| A label repeated **across operands** | those axes are aligned and multiplied elementwise |
| A label **missing from the output** | that axis is summed (contracted) away |
| A label repeated **within one operand** | take the diagonal along those axes |

The order of the labels on the right of `->` sets the axis order of the result, so transposition is free — it is just a relabelling.

In full generality, for operands $A^{(1)}, \dots, A^{(P)}$ with output labels $S$ and contracted labels $T$:

$$
O_{S} = \sum_{T} \prod_{p=1}^{P} A^{(p)}_{\,\text{labels}(p)}
$$

Every operation below — matmul, transpose, trace, outer product, attention — is a special case of that one expression. The value of einsum is that it makes the contraction explicit instead of hiding it behind a function name and an axis convention.

> Each cell below is self-contained: it builds its own inputs, so cells can be run in any order. Small integer arrays are used throughout so the results can be checked by hand.

### Matrix Multiplication

$$
C_{ij} = \sum_{k} A_{ik} B_{kj}
$$

The label $k$ appears in both operands but not in the output, so it is the **contracted** axis: the two matrices are aligned along it and summed over. The labels $i$ and $j$ appear in the output, so they are carried through — one output element per $(i, j)$ pair.

Shapes must agree on the contracted label: $(M \times K) \cdot (K \times N) \rightarrow (M \times N)$. Cost is $\mathcal{O}(MKN)$ — one multiply-add per $(i, j, k)$ triple.

This is exactly what `A @ B` does; einsum just names the axes instead of relying on the positional convention that matmul contracts the last axis of the left operand against the second-to-last of the right.

```python
import numpy as np

A = np.arange(6).reshape(3, 2)      # (3, 2)
B = np.arange(8).reshape(2, 4)      # (2, 4)

M = np.einsum('ik,kj->ij', A, B)    # contract over k
print(M)
print(np.allclose(M, A @ B))        # same as the @ operator
```

### Outer Product

$$
M_{ij} = a_i b_j
$$

No label is shared between the operands, so **nothing is contracted** — every element of $a$ meets every element of $b$. The result gains an axis rather than losing one: $(M,) \times (N,) \rightarrow (M \times N)$.

This is the instructive contrast with the dot product further down. Same two vectors, same subscripts on the inputs; the only difference is whether the shared label survives into the output. Keep both labels and you get the outer product; share one label and drop it and you get the inner product.

```python
import numpy as np

a = np.array([1, 2, 3])             # (3,)
b = np.array([10, 20])              # (2,)

outer = np.einsum('i,j->ij', a, b)  # no shared label -> nothing summed
print(outer)
print(np.allclose(outer, np.outer(a, b)))
```

### Transpose

$$
(X^{\top})_{ji} = X_{ij}
$$

Pure relabelling: the same labels appear on both sides of the arrow, just in a different order. No multiplication, no summation — only a permutation of the axes. NumPy can satisfy this by adjusting strides rather than moving data.

The same trick generalizes to any permutation of any rank, which is where einsum beats chained `.transpose()` calls for readability: `'ijk->kij'` says what it does.

```python
import numpy as np

X = np.arange(6).reshape(2, 3)      # (2, 3)

Xt = np.einsum('ij->ji', X)         # reorder the labels
print(Xt)
print(np.allclose(Xt, X.T))
```

### Sum of All Elements

$$
s = \sum_{i} \sum_{j} X_{ij}
$$

The output subscript is **empty**, so every label is dropped and therefore summed. The result is a scalar — a full reduction over the array.

This is the limiting case of the "missing from the output means summed" rule: drop everything and nothing is left to index.

```python
import numpy as np

X = np.arange(6).reshape(2, 3)      # (2, 3)

total = np.einsum('ij->', X)        # empty output -> sum over i and j
print(total)
print(np.allclose(total, X.sum()))
```

### Column-wise Sum

$$
c_j = \sum_{i} X_{ij}
$$

A partial reduction: $i$ is dropped so it is summed over, while $j$ survives. Summing over the row index collapses the rows, leaving one value per column — shape $(M \times N) \rightarrow (N,)$.

Note that the notation names the axis you *keep*, whereas `X.sum(axis=0)` names the axis you *remove*. For rank-2 arrays that is a wash, but on a rank-5 tensor `'bhqkd->bhd'` is considerably easier to read than a tuple of axis numbers.

```python
import numpy as np

X = np.arange(6).reshape(2, 3)      # (2, 3)

col_sums = np.einsum('ij->j', X)    # i dropped -> summed over rows
print(col_sums)
print(np.allclose(col_sums, X.sum(axis=0)))
```

### Matrix Multiplication with a Transposed Operand

$$
C_{ik} = \sum_{j} X_{ij} V_{kj} \qquad \text{i.e.} \qquad C = X V^{\top}
$$

Here the shared label $j$ sits in the **second** axis of both operands, so the contraction runs along matching axes without either matrix needing to be transposed first. Shapes: $(M \times D)$ and $(N \times D) \rightarrow (M \times N)$.

This pattern is worth internalizing because it is the shape of a similarity matrix — every row of $X$ dotted against every row of $V$ — and therefore the core of the $QK^{\top}$ term in attention. Expressing it directly avoids materializing an intermediate transpose.

```python
import numpy as np

X = np.arange(6).reshape(2, 3)      # (2, 3) -- 2 rows of length 3
V = np.arange(9).reshape(3, 3)      # (3, 3) -- 3 rows of length 3

C = np.einsum('ij,kj->ik', X, V)    # contract over the shared trailing axis
print(C)
print(np.allclose(C, X @ V.T))
```

### Vector Dot Product

$$
s = \sum_{i} a_i b_i
$$

One shared label, dropped from the output: the vectors are multiplied elementwise and the result summed to a scalar.

Compare directly against the outer product above — `'i,j->ij'` versus `'i,i->'`. Reusing the *same* letter forces the axes to align pairwise instead of forming all combinations, and omitting it from the output collapses the result.

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

dot = np.einsum('i,i->', a, b)      # shared label, dropped -> scalar
print(dot)                          # 1*4 + 2*5 + 3*6 = 32
print(np.allclose(dot, np.dot(a, b)))
```

### Frobenius Inner Product

$$
\langle A, B \rangle_F = \sum_{i} \sum_{j} A_{ij} B_{ij} = \mathrm{tr}\!\left(A^{\top} B\right)
$$

The dot product generalized to matrices: multiply elementwise, then sum every entry. Both labels are shared and both are dropped, so a rank-2 pair reduces to a scalar.

Taking $B = A$ gives the squared Frobenius norm:

$$
\|A\|_F^2 = \sum_{i} \sum_{j} A_{ij}^2
$$

which is the quantity behind weight decay and most matrix-reconstruction losses.

```python
import numpy as np

A = np.arange(6).reshape(2, 3)
B = np.arange(6, 12).reshape(2, 3)

frob = np.einsum('ij,ij->', A, B)   # both labels shared and dropped
print(frob)
print(np.allclose(frob, np.trace(A.T @ B)))

sq_norm = np.einsum('ij,ij->', A, A)
print(sq_norm, np.allclose(sq_norm, np.linalg.norm(A) ** 2))
```

### Element-wise (Hadamard) Product

$$
(A \circ B)_{ij} = A_{ij} B_{ij}
$$

Both labels are shared — so the operands align elementwise — but both also appear in the output, so **nothing is summed**. Shape is preserved: $(M \times N) \rightarrow (M \times N)$.

Set this beside the Frobenius product above: identical input subscripts, and the only difference is whether the labels survive the arrow. Keeping them gives the elementwise product; dropping them sums that same product to a scalar. This is the clearest demonstration that in einsum, multiplication is decided by the inputs and summation is decided by the output.

```python
import numpy as np

A = np.arange(6).reshape(2, 3)
B = np.arange(6, 12).reshape(2, 3)

had = np.einsum('ij,ij->ij', A, B)  # labels kept -> no summation
print(had)
print(np.allclose(had, A * B))
```

### Diagonal Extraction

$$
d_i = A_{ii}
$$

The label $i$ is repeated **within a single operand**, which selects the entries where both axes carry the same index — the diagonal. This is the one rule that has no equivalent in ordinary matmul notation, and it works only on axes of equal length.

Drop the label from the output as well and the diagonal is summed, giving the trace:

$$
\mathrm{tr}(A) = \sum_{i} A_{ii}
$$

```python
import numpy as np

A = np.arange(9).reshape(3, 3)
print(A)

diag = np.einsum('ii->i', A)        # repeated label within one operand
print(diag)
print(np.allclose(diag, np.diag(A)))

trace = np.einsum('ii->', A)        # ... and dropped -> trace
print(trace, np.allclose(trace, np.trace(A)))
```

### Batched Matrix Multiplication

Given a stack of $B$ matrices $A_1, \dots, A_B$ with $A_b \in \mathbb{R}^{M \times K}$, and a second stack $V_1, \dots, V_B$ with $V_b \in \mathbb{R}^{K \times N}$, batched matmul applies an independent matrix product per batch element:

$$
C_b = A_b V_b \in \mathbb{R}^{M \times N}, \qquad b = 1, \dots, B
$$

The batch axis is a *spectator*: it is carried through untouched while the contraction happens only over the shared inner dimension. Total cost is $B$ times a single matmul, $\mathcal{O}(BMKN)$.

**Sources**

- [`numpy.matmul`](https://numpy.org/doc/stable/reference/generated/numpy.matmul.html) — stacks of matrices are treated as elements residing in the last two indexes and broadcast accordingly.
- [`numpy.einsum`](https://numpy.org/doc/stable/reference/generated/numpy.einsum.html) — the general Einstein-summation interface.
- [cuBLAS `gemmStridedBatched`](https://docs.nvidia.com/cuda/cublas/#cublas-t-gemmstridedbatched) — the BLAS-level primitive this maps onto in practice.

```python
import numpy as np

B, M, K, N = 5, 3, 4, 6             # batch, rows, contracted dim, cols

A_BMK = np.random.rand(B, M, K)     # (5, 3, 4) -- a stack of B (M x K) matrices
V_BKN = np.random.rand(B, K, N)     # (5, 4, 6) -- a stack of B (K x N) matrices

# b is a spectator: shared by both operands AND kept in the output, so it is
# aligned but never summed -- one independent matmul per batch element.
# k is shared and dropped, so it is the contracted axis.
C_BMN = np.einsum('bmk,bkn->bmn', A_BMK, V_BKN)

print(C_BMN.shape)                          # (5, 3, 6)
print(np.allclose(C_BMN, A_BMK @ V_BKN))    # @ broadcasts over the leading axes
```

### Attention

**Scaled dot-product attention.** With queries $Q \in \mathbb{R}^{n \times d_k}$, keys $K \in \mathbb{R}^{m \times d_k}$, and values $V \in \mathbb{R}^{m \times d_v}$:

$$
\mathrm{Attention}(Q, K, V) = \mathrm{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right) V
$$

The $1/\sqrt{d_k}$ factor counteracts the growth of the dot products with dimension, which would otherwise push the softmax into regions of vanishing gradient.

Written per row, with $\alpha_{ij}$ the attention weight of query $i$ over key $j$:

$$
\alpha_{ij} = \frac{\exp\!\left(q_i \cdot k_j / \sqrt{d_k}\right)}{\sum_{j'} \exp\!\left(q_i \cdot k_{j'} / \sqrt{d_k}\right)},
\qquad
o_i = \sum_j \alpha_{ij}\, v_j
$$

**Multi-head attention.** Each of the $h$ heads projects into its own subspace, attends independently, and the results are concatenated and mixed:

$$
\mathrm{head}_i = \mathrm{Attention}\!\left(QW_i^{Q},\, KW_i^{K},\, VW_i^{V}\right)
$$

$$
\mathrm{MultiHead}(Q, K, V) = \mathrm{Concat}(\mathrm{head}_1, \dots, \mathrm{head}_h)\, W^{O}
$$

with $W_i^{Q}, W_i^{K} \in \mathbb{R}^{d_{\text{model}} \times d_k}$, $W_i^{V} \in \mathbb{R}^{d_{\text{model}} \times d_v}$, and $W^{O} \in \mathbb{R}^{h d_v \times d_{\text{model}}}$. The original paper uses $h = 8$ and $d_k = d_v = d_{\text{model}}/h = 64$.

For causal (decoder) attention, an additive mask $M_{ij} = -\infty$ for $j > i$ is applied to the scores before the softmax.

**Sources**

- Vaswani et al., *Attention Is All You Need* (2017) — [arXiv:1706.03762](https://arxiv.org/abs/1706.03762). §3.2.1 scaled dot-product attention, §3.2.2 multi-head attention.
- Bahdanau, Cho & Bengio, *Neural Machine Translation by Jointly Learning to Align and Translate* (2014) — [arXiv:1409.0473](https://arxiv.org/abs/1409.0473). The additive-attention predecessor.
- Luong, Pham & Manning, *Effective Approaches to Attention-based Neural Machine Translation* (2015) — [arXiv:1508.04025](https://arxiv.org/abs/1508.04025). Introduces the multiplicative ("dot-product") form.

```python
import numpy as np

N, M, K, V = 3, 5, 4, 6             # queries, keys/values, key dim, value dim

q_NK = np.random.rand(N, K)         # (3, 4) -- one query row per output position
k_MK = np.random.rand(M, K)         # (5, 4) -- one key row per source position
v_MV = np.random.rand(M, V)         # (5, 6) -- one value row per source position


def softmax(x, axis=-1):
    x = x - np.max(x, axis=axis, keepdims=True)   # shift for numerical stability
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)


# K is shared and dropped -> every query dotted against every key.
# Scaling by sqrt(K) keeps the logits from growing with the key dimension.
logits_NM = np.einsum('NK,MK->NM', q_NK, k_MK) / np.sqrt(K)
weights_NM = softmax(logits_NM, axis=-1)            # normalize over keys

# M is shared and dropped -> each output row is a weighted sum of value rows.
out_NV = np.einsum('NM,MV->NV', weights_NM, v_MV)

print(out_NV.shape)                                 # (3, 6)
print(np.allclose(weights_NM.sum(axis=-1), 1))      # each query's weights sum to 1
```

```python
import numpy as np

N, M, D, K, V, H = 3, 5, 4, 4, 6, 8   # queries, keys, model dim, key dim, value dim, heads


def softmax(x, axis=-1):
    x = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)


# Inputs live in model space (D); each head projects them into its own subspace.
q_ND = np.random.rand(N, D)
k_MD = np.random.rand(M, D)
v_MD = np.random.rand(M, D)

wq_HDK = np.random.rand(H, D, K)      # per-head query projection
wk_HDK = np.random.rand(H, D, K)      # per-head key projection
wv_HDV = np.random.rand(H, D, V)      # per-head value projection
wo_HVD = np.random.rand(H, V, D)      # W^O, the (H*V, D) output matrix as (H, V, D)

# D is contracted; H appears only in the weights, so it is carried into the
# output -- one projected copy of the input per head.
q_HNK = np.einsum('ND,HDK->HNK', q_ND, wq_HDK)
k_HMK = np.einsum('MD,HDK->HMK', k_MD, wk_HDK)
v_HMV = np.einsum('MD,HDV->HMV', v_MD, wv_HDV)


def attention_logits(q_HNK, k_HMK, causal=False):
    """Scaled dot-product scores. causal=True forbids attending to the future."""
    N, K = q_HNK.shape[-2], q_HNK.shape[-1]
    M = k_HMK.shape[-2]
    logits_HNM = np.einsum('HNK,HMK->HNM', q_HNK, k_HMK) / np.sqrt(K)
    if causal:
        # k=M-N aligns the diagonal when there are more keys than queries
        # (cached decoding); it reduces to k=0 when M == N.
        mask_NM = np.tri(N, M, k=M - N, dtype=bool)     # (N, M) broadcasts over H
        logits_HNM = np.where(mask_NM, logits_HNM, -np.inf)
    return logits_HNM


logits_HNM = attention_logits(q_HNK, k_HMK, causal=False)
weights_HNM = softmax(logits_HNM, axis=-1)

# H is contracted here: summing each head's projected output over H is exactly
# equivalent to concatenating the heads and applying a single (H*V, D) matrix.
out_ND = np.einsum('HNM,HMV,HVD->ND', weights_HNM, v_HMV, wo_HVD)

print(out_ND.shape)                                     # (3, 4) -- back in model space
print(np.allclose(weights_HNM.sum(axis=-1), 1))         # weights normalize per query

# The concat-then-project form, written out, to confirm the H-contraction above.
heads_NHV = np.einsum('HNM,HMV->NHV', weights_HNM, v_HMV)
print(np.allclose(out_ND, heads_NHV.reshape(N, H * V) @ wo_HVD.reshape(H * V, D)))

# Causal masking: nothing above the shifted diagonal, rows still normalize.
causal_HNM = softmax(attention_logits(q_HNK, k_HMK, causal=True), axis=-1)
print(np.allclose(np.triu(causal_HNM, k=M - N + 1), 0))
print(np.allclose(causal_HNM.sum(axis=-1), 1))
```

#### Contraction Order

`np.einsum` with three or more operands has a choice to make. By default it evaluates the expression literally: one fused loop nest over every unique label, costing $\mathcal{O}(HNMVD)$ for the attention contraction above. Passing `optimize` instead reduces the expression to a sequence of **pairwise** contractions, each of which can be dispatched to BLAS — the source of most of the speedup, beyond the FLOP saving itself.

Two effects are worth separating, because they pull in opposite directions:

- **`optimize=True` re-plans on every call.** Path search is pure Python and costs a fixed ~10–20 µs regardless of tensor size. Below that threshold the planning costs more than the contraction saves, so the default (`optimize=False`) is genuinely faster on small tensors.
- **`optimize=True` searches greedily**, which is not always the best order. `optimize='optimal'` searches exhaustively — affordable for three or four operands, factorial beyond that.

Computing the path once with `einsum_path` and passing it back into `einsum` avoids both problems: no per-call planning, and the better order. `einsum_path` reads only `.shape` and performs no arithmetic, so the plan stays valid for as long as the shapes do.

The tradeoff is memory. The naive loop allocates nothing; a pairwise plan materializes intermediates, which is what `Largest intermediate` in the path report measures.

At this notebook's toy sizes the naive form wins and greedy and optimal happen to agree — the cell below shows both, and shows them diverging once $V$ is large relative to $D$.

```python
# Plan once, outside the hot loop. Depends only on shapes, not values.
attn_path, path_info = np.einsum_path(
    'HNM,HMV,HVD->ND', weights_HNM, v_HMV, wo_HVD, optimize='optimal'
)
print(attn_path)        # the plan: which operand pair to contract, in order
print(path_info)        # FLOP counts, scaling, largest intermediate

out_fast_ND = np.einsum('HNM,HMV,HVD->ND', weights_HNM, v_HMV, wo_HVD, optimize=attn_path)
print(np.allclose(out_fast_ND, out_ND))   # same answer, different contraction order

# At these toy shapes greedy and optimal agree. They diverge once V grows large
# relative to D: then folding W^O into the values first collapses V immediately,
# a path optimal finds and greedy (what optimize=True uses) does not.
big = (np.empty((H, 512, 512)), np.empty((H, 512, 64)), np.empty((H, 64, D)))
print(np.einsum_path('HNM,HMV,HVD->ND', *big, optimize='greedy')[0])
print(np.einsum_path('HNM,HMV,HVD->ND', *big, optimize='optimal')[0])

# %timeit np.einsum('HNM,HMV,HVD->ND', weights_HNM, v_HMV, wo_HVD)
# %timeit np.einsum('HNM,HMV,HVD->ND', weights_HNM, v_HMV, wo_HVD, optimize=True)
# %timeit np.einsum('HNM,HMV,HVD->ND', weights_HNM, v_HMV, wo_HVD, optimize=attn_path)
```

### Mixture of Experts

A MoE layer holds $n$ expert networks $E_1, \dots, E_n$ and a gating network $G$ that produces a distribution over them. The layer output is the gate-weighted combination of expert outputs:

$$
y = \sum_{i=1}^{n} G(x)_i \, E_i(x)
$$

Each expert is an ordinary two-layer feed-forward network with its own weights, and the gate is a softmax over a learned projection:

$$
E_i(x) = \mathrm{relu}\!\left(x W^{(1)}_i\right) W^{(2)}_i,
\qquad
G(x) = \mathrm{softmax}\!\left(x W_g\right)
$$

This is the dense form: every expert is evaluated for every token, and the gate decides only how much each contributes. There is no computational saving here — cost is $n$ experts per token. The saving comes from making $G(x)$ sparse (keep the top $k$ logits, zero the rest) so that most experts can be skipped, which is what the sparsely-gated and Switch variants do. Written densely first, that optimization is easy to see as a modification of one line rather than a different algorithm.

**Notation.** Following the shape-suffix convention used above, with letters chosen not to collide with the attention cells — $M$ is already keys and $H$ is already heads there, so the expert hidden dimension takes $F$ and the model dimension stays $D$:

| Label | Meaning |
| --- | --- |
| $S$ | tokens |
| $D$ | model dimension |
| $E$ | experts |
| $F$ | expert hidden dimension |

The whole layer is three contractions. The gate contracts $D$ to score every token against every expert, giving $(S, E)$. The expert body applies both weight matrices with $E$ as a **spectator** axis — shared between operands and kept in the output, exactly like the batch axis in batched matmul — so every token flows through all $E$ experts in parallel, giving $(S, E, D)$. The combination then contracts $E$ away against the gate scores, weighting each expert's output and summing to $(S, D)$.

That last step is the one worth pausing on: it is the same "share a label, drop it from the output" pattern as the dot product, just applied to whole expert outputs instead of scalars.

**Sources**

- Jacobs, Jordan, Nowlan & Hinton, *Adaptive Mixtures of Local Experts* (1991), *Neural Computation* 3(1):79–87 — [doi:10.1162/neco.1991.3.1.79](https://doi.org/10.1162/neco.1991.3.1.79). The original MoE, in the dense form above.
- Shazeer et al., *Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer* (2017) — [arXiv:1701.06538](https://arxiv.org/abs/1701.06538). §2.1, where the gate becomes sparse and the layer stops evaluating every expert.

```python
# Dense MoE: every expert runs on every token; the gate sets the weights.

S, D, E, F = 8, 4, 4, 16            # tokens, model dim, experts, expert hidden

x_SD = np.random.rand(S, D)
wg_DE = np.random.rand(D, E)        # router
w1_EDF = np.random.rand(E, D, F)    # per-expert up-projection
w2_EFD = np.random.rand(E, F, D)    # per-expert down-projection

# D dropped -> a distribution over experts per token
gates_SE = softmax(np.einsum('SD,DE->SE', x_SD, wg_DE), axis=-1)

# E is a spectator -> every token through every expert
h_ESF = np.maximum(np.einsum('SD,EDF->ESF', x_SD, w1_EDF), 0)
experts_ESD = np.einsum('ESF,EFD->ESD', h_ESF, w2_EFD)

# E dropped -> gate-weighted sum of each token's E proposals
out_SD = np.einsum('SE,ESD->SD', gates_SE, experts_ESD)

print(out_SD.shape)                             # (8, 4) -- same space as the input
print(np.allclose(gates_SE.sum(axis=-1), 1))    # gates form a distribution
```
