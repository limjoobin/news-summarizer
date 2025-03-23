FROM python:3.12-slim-bookworm AS base
COPY --from=ghcr.io/astral-sh/uv:0.6.2 /uv /uvx /bin/

# Compile Python source files to byte code (improve startup time, but increase installation time)
# Also reuse layers from the cache to speed up performance across builds
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy