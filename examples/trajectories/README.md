# Example Agent Trajectories

A small curated set of agent execution logs from the benchmark — one to three
trajectories per scaffold (Codex CLI, Claude Code, OpenHands, Gemini CLI),
sampled across difficulty. Each trajectory shows an agent reading a problem,
iterating over edits/builds/local tests, submitting to the OJ, reading back
verdicts, and either improving or stopping.

The full per-(scaffold, model, problem) log set is much larger; this directory
exists so reviewers can sanity-check what a "trajectory" looks like in this
benchmark without cloning the entire log archive.

## Anonymization

These logs have been scrubbed before inclusion:

- Personal access tokens (`ghp_*`, `gho_*`, ...) replaced with `<GH_TOKEN>`.
- ACMOJ submission tokens (`acmoj-<32-hex>`) replaced with `<OJ_TOKEN>`.
- Internal absolute paths under the original `/data2/<user>/...` prefix were
  rewritten to `<repo>/...`.
- Personal email addresses and handles rewritten to `<anon>` placeholders.

The agent-side `GITHUB_USER` value `ojbench` is the public benchmark org
account and was left as-is.

## Layout

```
trajectories/
├── codex_cli/<model>/<problem>/{run.log, submission_ids.log}
├── claude_code/<model>/<problem>/{run.log, submission_ids.log}
├── openhands/<model>/<problem>/{run.log, submission_ids.log}
└── gemini_cli/<model>/<problem>/{run.log, submission_ids.log}
```

`run.log` is the agent's main stdout/stderr trace for that one problem.
`submission_ids.log` is the JSONL record of OJ submissions made during the run
(timestamp + submission_id) — useful for cross-referencing verdicts on the OJ.

## Index

| Scaffold | Model | Problem (ACMOJ) | Score | #Subs | What's interesting |
|---|---|---|---|---|---|
| Codex CLI | GPT-5 | 004 *Bookstore* (1075/1775) | 94 | 2 | Multi-subproblem (2 ACMOJ tasks); agent designs persistent .db storage to handle stateful test sequences across runs. |
| Codex CLI | GPT-5 | 038 *vector++* (2609) | 95 | 4 | Performance-critical custom `std::vector`; agent iterates 4 times tightening allocator / move semantics, going from WA-heavy to majority-accepted testpoints. |
| Codex CLI | Sonnet-4.5 | 044 *小可怜的字符串* (14297) | 80 | 2 | String/algorithmic problem; agent profiles locally before each submission. |
| Codex CLI | Gemini-3-Flash | 049 *迅影的机器人* | 99 | 5 | Five submissions chasing the last 1%; example of agent stopping mid-debug after diminishing returns. |
| Claude Code | Sonnet-4.5 | 004 *Bookstore* (1075/1775) | 97 | 5 | Same multi-subproblem as above; full implementation of an account/book/log subsystem in C++ from scratch. |
| Claude Code | Sonnet-4.5 | 036 *T3* (2578) | 90 | 3 | Three-submission iteration; mid-difficulty algorithmic problem. |
| Claude Code | GPT-5 | 038 *vector++* (2609) | 89 | 4 | Comparable run to the Codex+GPT-5 trajectory above on the same problem — useful for scaffold-vs-scaffold comparison with the same model family. |
| Claude Code | Gemini-3-Flash | 038 *vector++* (2609) | 98 | 5 | Strong performance from a smaller model on the perf-vector task; iterates on cache locality. |
| OpenHands | Sonnet-4.5 | 007 *BASIC Interpreter* (2510) | 99 | 5 | Large existing C++ codebase to extend — agent navigates Stanford CPP lib + parser/eval files; 5 submissions tighten edge cases. |
| OpenHands | Sonnet-4.5 | 038 *vector++* (2609) | 97 | 5 | Small driver log (heavy reasoning lives in OpenHands' internal trajectory); 5 submissions, ends with 97/100. |
| OpenHands | GLM-4.6 | 028 (ACMOJ 1346) | 90 | 5 | Open-weight model on a mid-difficulty task; 5 submissions, lands at 90. |
| OpenHands | qwen3-235b | 033 (ACMOJ 2100) | n/a | 2 | Supplementary raw-log example (not in the curated final-logs set); shows OpenHands+qwen3 on a problem the agent submitted to twice. |
| Gemini CLI | Gemini-3-Flash | 036 *T3* (2578) | 90 | 3 | Best Gemini-CLI run in the index; clean 3-submission progression. |
| Gemini CLI | Gemini-3-Flash | 049 *迅影的机器人* (2571) | 42 | 2 | Partial-credit failure case — agent stops at 42/100 after two attempts. Useful as a *negative* example of what the harness does when a model gives up early. |

## Notes

- Scores are the per-problem normalized scores from the OJ (max across valid
  submissions; see the manifest in the parent log archive for details).
- `#Subs` is the number of OJ submissions actually recorded for the run; the
  per-problem cap was 8.
- `Score` n/a means the supplementary trajectory was sampled from raw logs
  (not the curated final-log set), so no aggregated score is published.
- Trajectories were chosen to span easy/hard problems and to include at least
  one debugging-heavy run per scaffold; runs that bottomed out due to API
  503s, billing/quota, or auth errors were filtered out.
