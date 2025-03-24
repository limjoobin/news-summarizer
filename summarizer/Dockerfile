FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Disable Python Downloads
ENV UV_PYTHON_DOWNLOADS=0
# Compile Python source files to byte code (improve startup time, but increase installation time)
ENV UV_COMPILE_BYTECODE=1 
# Also reuse layers from the cache to speed up performance across builds
ENV UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies. This layer is cached, so it does not run again if there are no changes
# to the dependencies, which happen less often than source code changes
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Add the project source code and install it. # If there are any changes to the application 
# source code, this layer's cache is invalidated, but not the dependencies layer (previous layer)
# TODO: FIX DOCKERIGNORE TO IGNORE .VENV, due to some incompatibilities between wsl2 and windows, the windows OS is unable
# to access some files used by wsl2. For now, comment this out, there should be no big difference (so long as no changes to src code)
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Multi-stage build
FROM python:3.12-slim-bookworm

WORKDIR /app

#COPY --from=builder --chown=app:app /app /app
COPY --from=builder /app/.venv .venv
# Only need the src code
COPY --from=builder /app/src /app

# Expose port 8000, which is where the app is hosted
EXPOSE 8000

# To use the virtual environment from the project
ENV PATH="/app/.venv/bin:$PATH"

CMD uvicorn main:app --host 0.0.0.0 --port 8000

    
