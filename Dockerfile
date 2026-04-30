FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    libx11-6 libxcursor1 libxi6 libxrandr2 libgl1 libfontconfig1 \
    libstdc++6 libgcc-s1 xvfb \
    && rm -rf /var/lib/apt/lists/*

ARG ASEPRITE_DEB=aseprite_1.3.17.2_amd64.deb
COPY ${ASEPRITE_DEB} /tmp/aseprite.deb
RUN dpkg -i /tmp/aseprite.deb && rm /tmp/aseprite.deb

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY . .
RUN uv export --frozen --no-dev --no-emit-project -o requirements.txt \
    && uv pip install --system --no-cache -r requirements.txt \
    && pip install --no-cache-dir .

FROM base AS runtime

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/aseprite-mcp /usr/local/bin/aseprite-mcp
COPY --from=builder /app /app

WORKDIR /app

ENV ASEPRITE_PATH=/usr/bin/aseprite
ENV ASEPRITE_WS_HOST=0.0.0.0
ENV ASEPRITE_WS_PORT=8765
ENV ASEPRITE_OUTPUT_DIR=/app/generated_assets
ENV DISPLAY=:99

EXPOSE 8080 8765

ENTRYPOINT ["./docker-entrypoint.sh"]