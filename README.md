# python-notes

Notes and exercises on the Python → NumPy → JAX path toward writing kernels.
Setup lives in [SETUP.md](SETUP.md).

## Topics covered

### [Object Model](Object%20Model/) — why pure-Python numerics are slow
- What `x = 5` actually stores: boxed `PyObject`s, small-int caching, `id`/`sys.getsizeof`
- Why iterating a NumPy array element-by-element is slower than a list: re-boxing on every access
- `Counter` vs a hand-written counting loop — bytecode inspection (`dis`), correctness check, timing sweep, plots
- Reading a `cProfile` dump (`stats.out`)

### [NumPy](NumPy/) — the array mental model
- [From Python to NumPy](https://www.labri.fr/perso/nrougier/from-python-to-numpy/): `ndarray` as a contiguous buffer + strides, vectorization, Mandelbrot as temporal vectorization
- [100 NumPy exercises](https://github.com/rougier/numpy-100): indexing, broadcasting, structured dtypes, strides, reductions along axes
- [Einsum](NumPy/einsum.md): contraction notation from first principles — matmul, transpose, trace, outer product, batched contractions, attention

### [JAX](JAX/)
- Quickstart: `jnp` vs `np` duck-typing, immutability and `.at[].set()`, `block_until_ready()` for honest timing
- [`jit`](JAX/jit.ipynb): trace → compile → cache, and why control flow on traced values fails
- [Autodiff](JAX/autodiff.ipynb): `grad` on a linear logistic regression
- [Auto-vectorization](JAX/auto_vec.ipynb): manual batching vs `vmap`
- [Pytrees](JAX/pytrees.ipynb): nested containers as the parameter representation
- [Sharp bits](JAX/sharp_bits.ipynb): impure functions, side effects firing once at trace time

### [Scaling Book](Scaling%20Book/)
- [Roofline](Scaling%20Book/roofline.ipynb): arithmetic intensity vs memory bandwidth, achieved FLOPs/s against batch size on TPU v5e

### [OOP](OOP/)
- [Classes and `__init__`](OOP/intro.md), instance vs class attributes, attribute lookup and shadowing ([data_attributes](OOP/data_attributes/data_attributes.md))
- Methods: instance/class/static, dunder methods — `Stack`, `Pizza`, `FibonacciIterator`
- [Conveyor-belt sushi restaurant](OOP/conveyor_belt/): a multi-module simulation (plates, tickets, pricing, chef, belt) as the composition exercise
