# Learning JAX (kernel focus)

## Python Fundamentals

**Execution & memory model**
- [x] CPython object model: boxed PyObjects, why pure-Python numeric loops are 100–1000× slower
- [ ] The GIL: what it blocks, why it's irrelevant once work is in XLA/CUDA, but relevant for host dispatch overhead
- [x] Memory: contiguous buffers vs lists, the buffer protocol

**Language machinery you'll read in JAX source**
- [x] Decorators (jit/pmap are decorators)
- [ ] Closures & cell variables (how traced fns capture constants)
- [ ] functools (partial, wraps) — static-argument patterns

**Static vs dynamic values**
- [ ] Python ints as compile-time constants vs traced arrays
- [x] Why control flow on traced values fails → bridges to JAX control flow

## NumPy Fundamentals

- [x] [From Python to Numpy](https://www.labri.fr/perso/nrougier/from-python-to-numpy/)
- [ ] [numpy-100](https://github.com/rougier/numpy-100)
- [ ] Einsum fluency: attention, batched matmul, MoE dispatch/combine as einsums
- [ ] Fancy indenxing, boolean masks, axis reasoning (argmax/sum/mean along axes)
- [ ] Reimplement from scratch:
    - [ ] softmax
    - [ ] layernorm
    - [ ] conv (im2col)
    - [ ] top-k
    - [ ] one-hot

## JAX Fundamentals

**Tracing & abstract values** *(the conceptual heart)*
- [x] Tracers: jit runs your fn with abstract stand-ins
- [ ] ShapedArray / abstract eval: shapes & dtypes known at trace time, values are not
- [x] Side effects (print) fire once at trace time
- [ ] Concrete vs abstract: when JAX needs a real value

**jaxprs — the IR you must learn to read**
- [x] jax.make_jaxpr() to inspect the trace
- [ ] Anatomy: invars, eqns, primitives, outvars
- [ ] Your primary debugging substrate

**The transformation stack**
- [x] jit (trace → compile → cache)
- [ ] grad / vjp / jvp (autodiff as a trace transform — your kernels need backward passes)
- [x] vmap (batching as a transform; the batching-rule idea reappears in Pallas)
- [ ] Composition: jit(grad(vmap(f)))

**Control flow & data layout** *(daily kernel tools)*
- [ ] lax.scan (the workhorse — sequential loops → one op; attention, accumulation)
- [ ] lax.cond / select / while_loop
- [ ] lax.dynamic_slice / dynamic_update_slice (THE tiling primitives — load/store a block)
- [ ] gather/scatter and why they're expensive
- [x] .at[].set() functional updates

**Primitives & the extension system**
- [ ] What a primitive is (atomic ops jaxprs are built from)
- [ ] bind / abstract_eval / impl rules
- [ ] Custom primitives → the bridge to custom kernels

**Compilation & the XLA boundary** *(layer under your kernels)*
- [ ] HLO as the lower IR (jaxpr → HLO → device code)
- [ ] Dumping & reading HLO (xla_dump flags)
- [ ] Op fusion: when XLA fuses for free → tells you which kernels are NOT worth hand-writing
- [ ] Compilation lifecycle: trace → lower → compile → execute
- [ ] Recompilation triggers (shape/dtype/static_argnums)
- [ ] Donated buffers, in-place via XLA
- [ ] Async execution: Python returns early, device runs ahead → implications for benchmarking
- [ ] block_until_ready() — timing correctly
- [ ] Device arrays, committed placement, transfers

**Profiling**
- [ ] jax.profiler + trace viewer / Perfetto
- [ ] Reading a timeline: kernel time vs gaps vs host overhead
- [ ] Connecting roofline / arithmetic intensity to observed time

## Ecosystem (working knowledge, not depth)
- [ ] Flax NNX: modules as pytrees, nnx.split/merge, why it recovers purity
- [ ] State types: Param vs BatchStat vs RngState (the mutable-state answer)
- [ ] Linen (read-only literacy): init/apply, mutable collections — for MaxText etc.
- [ ] Optax: gradient transformations, chaining, opt_state threading
- [ ] nnx.jit + sharding interaction (feeds the sharded-transformer exercise)
- [ ] Exercise: port raw-JAX nanoGPT → NNX, diff what the framework absorbed

## Pallas
- [ ] Grid: launching over a tile-space (GPU blocks / TPU grid)
- [ ] BlockSpec: global arrays → per-program tiles (index_map = the tiling math)
- [ ] Refs: kernel sees mutable refs to on-chip blocks
- [ ] HBM vs SRAM/VMEM vs registers — minimize HBM traffic (your roofline made concrete)
- [ ] Explicit loads/stores between levels
- [ ] pallas_call: wiring the kernel into JAX
- [ ] Canonical kernel: fused attention — tiling Q/K/V, the online-softmax trick
- [ ] Why fusion avoids materializing the N×N matrix
- [ ] FlashAttention in Pallas — your headline artifact
- [ ] Backend awareness: GPU (Triton-like, software SRAM) vs TPU (Mosaic, VMEM + (8,128) layout)
- [ ] Crossover to Triton: same model (program_id, tl.load/store, masks), GPU-first, Pallas is the TPU bridge

## Foundational Models

For each of these, profile everything, and write gradient checks against finite differences or a PyTorch reference for each model.

- [ ] MLP on MNIST, pure JAX (no Flax/Optax). Hand-rolled params as pytrees, manual SGD, `jax.grad`, `vmap` over the batch instead of batched matmuls first, then compare.
- [ ] CNN (on CIFAR-10): Adds batch norm, a classic JAX pain point - mutable running statistics in a pure-functional world.
- [ ] GPT-2 style decoder-only transformer (nanoGPT-scale) Character-level Shakespeare, once in raw JAX, once in Flax NNX or Equinox. Include a KV cache for inference.
- [ ] Same transformer but sharded: Re-do with `jax.sharding` / `shard_map`
- [ ] Mixture-of-experts layer: Top-k routing, capacity factor, the dispatch/combine einsums.

## Capstone Project

- [ ] Every exercise in the [Scaling Book](https://jax-ml.github.io/scaling-book/)
- [ ] Addition transformer (~10M, jax_flax_optax, T4/TPU colab)
- [ ] Chinchilla derivation, dense vs MoE, from scratch: isoFLOP sweeps, honest noise discussion
- [ ] Pallas kernel beating `lax.ragged_dot` for `F > D` (fused up/down projection)