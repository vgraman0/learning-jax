

## JAX (everything JAX-specific lives here)

**Tracing & abstract values** *(the conceptual heart)*
- [ ] Tracers: jit runs your fn with abstract stand-ins
- [ ] ShapedArray / abstract eval: shapes & dtypes known at trace time, values are not
- [ ] Side effects (print) fire once at trace time
- [ ] Concrete vs abstract: when JAX needs a real value

**jaxprs — the IR you must learn to read**
- [ ] jax.make_jaxpr() to inspect the trace
- [ ] Anatomy: invars, eqns, primitives, outvars
- [ ] Your primary debugging substrate

**The transformation stack**
- [ ] jit (trace → compile → cache)
- [ ] grad / vjp / jvp (autodiff as a trace transform — your kernels need backward passes)
- [ ] vmap (batching as a transform; the batching-rule idea reappears in Pallas)
- [ ] Composition: jit(grad(vmap(f)))

**Control flow & data layout** *(daily kernel tools)*
- [ ] lax.scan (the workhorse — sequential loops → one op; attention, accumulation)
- [ ] lax.cond / select / while_loop
- [ ] lax.dynamic_slice / dynamic_update_slice (THE tiling primitives — load/store a block)
- [ ] gather/scatter and why they're expensive
- [ ] .at[].set() functional updates

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

**Pallas — writing the kernel** *(the destination)*
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