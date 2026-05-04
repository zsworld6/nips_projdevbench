# Claude Code Evaluation Docker Image

This image packages the project problems together with the collected agent
responses so that the Claude Code CLI can be used to re-run or analyse the
evaluations inside an isolated environment.

## Contents

- Ubuntu 24.04 base
- Node.js 20 and the `@anthropic-ai/claude-code` CLI
- Python 3 (with `requests`)
- Project directories:
  - `problem/`
  - `logs/`
  - `scripts/`
  - `config/`

## Build

From the repository root:

```bash
docker build \
  -f docker/llm-claude/Dockerfile \
  -t ojbench-llm-claude .
```

> 使用特定版本的 Claude Code CLI：
>
> ```bash
> docker build \
>   -f docker/llm-claude/Dockerfile \
>   --build-arg CLAUDE_CODE_VERSION=1.11.0 \
>   -t ojbench-llm-claude:1.11.0 .
> ```

## Run

```bash
docker run --rm -it ojbench-llm-claude
```

You will be dropped into `/opt/ojbench` as the non-root user `agent`.
Use the `claude` CLI (already installed globally) to run additional LLM
evaluation workflows.

The container provides `/opt/ojbench/cr_result` for storing evaluation output.
To persist results on the host, bind-mount a directory:

```bash
docker run --rm -it \
  -v "$(pwd)/cr_result:/opt/ojbench/cr_result" \
  ojbench-llm-claude
```

Files written under `/opt/ojbench/cr_result` inside the container will appear
in the host `cr_result/` directory.

