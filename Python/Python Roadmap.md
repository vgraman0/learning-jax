## Python foundations (substrate, kernel-relevant parts only)

**Execution & memory model**
- [x] CPython object model: boxed PyObjects, why pure-Python numeric loops are 100–1000× slower
- [ ] The GIL: what it blocks, why it's irrelevant once work is in XLA/CUDA, but relevant for host dispatch overhead
- [ ] Memory: contiguous buffers vs lists, the buffer protocol

**NumPy as the mental baseline**
- [ ] ndarray internals: shape, strides, dtype, views vs copies — strides are THE concept that carries into kernels
- [ ] Broadcasting rules (JAX inherits these exactly)
- [ ] Row-major (C) layout, what "contiguous" means for memory access / coalescing
- [ ] Vectorization: whole-array ops, not element loops

**Language machinery you'll read in JAX source**
- [ ] Decorators (jit/pmap are decorators)
- [ ] Closures & cell variables (how traced fns capture constants)
- [ ] functools (partial, wraps) — static-argument patterns

**Static vs dynamic values**
- [ ] Python ints as compile-time constants vs traced arrays
- [ ] Why control flow on traced values fails → bridges to JAX control flow