FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies, Node.js 20 and Python tooling
RUN apt-get update && \
    apt-get install -y curl ca-certificates gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y \
      git \
      python3 python3-pip \
      nodejs \
      build-essential \
      jq && \
    rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI (Anthropic) and basic Python deps
ARG CLAUDE_CODE_VERSION=2.0.37
RUN if [ "$CLAUDE_CODE_VERSION" = "latest" ]; then \
        npm install -g @anthropic-ai/claude-code; \
    else \
        npm install -g @anthropic-ai/claude-code@"$CLAUDE_CODE_VERSION"; \
    fi && \
    python3 -m pip install --break-system-packages requests

WORKDIR /opt/ojbench

# Copy project resources into the image
COPY problem ./problem
COPY logs ./logs
COPY scripts ./scripts
COPY config ./config
COPY README.md .

RUN mkdir -p /opt/ojbench/cr_result

# Create a non-root user
RUN useradd -m -s /bin/bash agent && \
    chown -R agent:agent /opt/ojbench

USER agent
ENV PATH="/home/agent/.local/bin:$PATH"

ENTRYPOINT ["/bin/bash"]

