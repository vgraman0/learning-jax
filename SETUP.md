# Setup

Dependencies are managed by [`uv`](https://docs.astral.sh/uv/). The manifest is
`pyproject.toml` and the exact pinned versions live in `uv.lock` (commit both).
This replaces a `requirements.txt`/`.env`-style file — `uv` is faster and the
lockfile makes the environment reproducible.

## Daily use

```bash
uv sync                 # create/update .venv to match the lockfile
uv run python foo.py    # run anything inside the env (no manual activate needed)
uv run jupyter lab      # launch JupyterLab
```

In a notebook, pick the **"LLM Kernels (JAX)"** kernel (already registered).

## Adding / removing packages

```bash
uv add <pkg>            # adds to pyproject.toml + lockfile + installs
uv remove <pkg>
uv sync --extra training --extra profiling   # pull optional groups
```

## What runs where

- **This Mac (Apple Silicon):** CPU JAX. Covers the whole roadmap up to Pallas —
  tracing, jaxprs, grad/jit/vmap, lax control flow, HLO dumping, profiling.
- **Pallas-GPU / Triton:** need NVIDIA GPU + CUDA → use **Colab** (free T4) or a
  Linux/NVIDIA cloud box. See the `gpu` extra in `pyproject.toml`.
- **Pallas-TPU:** needs a TPU VM (Colab TPU runtime works). See the `tpu` extra.

## Sanity check

```bash
uv run python -c "import jax; print(jax.__version__, jax.devices())"
# -> 0.10.2 [CpuDevice(id=0)]
```
