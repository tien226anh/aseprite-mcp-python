FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    libx11-6 libxcursor1 libxi6 libxrandr2 libgl1 libfontconfig1 \
    libstdc++6 libgcc-s1 xvfb \
    && rm -rf /var/lib/apt/lists/*

ARG ASEPRITE_DEB=aseprite_1.3.17.2_amd64.deb
COPY ${ASEPRITE_DEB} /tmp/aseprite.deb
RUN dpkg -i /tmp/aseprite.deb && rm /tmp/aseprite.deb

FROM base AS runtime

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev \
    && rm -rf /root/.cache/uv

ENV ASEPRITE_PATH=/usr/bin/aseprite
ENV ASEPRITE_WS_HOST=0.0.0.0
ENV ASEPRITE_WS_PORT=8765
ENV DISPLAY=:99

EXPOSE 8080 8765

ENTRYPOINT ["./docker-entrypoint.sh"]