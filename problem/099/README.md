# Problem 099 - 捕鱼达人

**OJ Problem ID**: 2454

## Table of Contents

- [Problem 099 - 捕鱼达人](#problem-099-捕鱼达人)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
    - [Background](#background)
  - [Assignment Description](#assignment-description)
    - [Grade Composition](#grade-composition)
  - [Assignment Requirements](#assignment-requirements)
    - [Input Format](#input-format)
    - [Output Format](#output-format)
    - [Samples](#samples)
    - [Data Constraints](#data-constraints)
  - [Per-Testcase Resource Limits](#per-testcase-resource-limits)
  - [Test Data](#test-data)
  - [Submission Requirements](#submission-requirements)
    - [OJ Git Repository Compilation Process](#oj-git-repository-compilation-process)
    - [Git Configuration Requirements](#git-configuration-requirements)
    - [Submission Guidelines](#submission-guidelines)
    - [Evaluation Notes](#evaluation-notes)
    - [Academic Integrity](#academic-integrity)

## Introduction

### Background

This problem tests algorithmic problem-solving skills.

## Assignment Description

### Grade Composition

| Grading Component | Percentage |
| :--: | :--: |
| Pass **2454. 捕鱼达人** | 80% |
| Code Review | 20% |

Here are several points that need clarification:

- In the Code Review, we will **strictly examine your code style and repository organization structure, etc.**

- This assignment provides some sample data for testing, stored in the `/workspace/data/099/data_test/` directory. Note that these are not the test cases on the Online Judge. Passing all local test cases does not guarantee that you will pass the OJ tests.

- Besides the provided sample data, we also encourage you to design your own test data based on your program logic to assist debugging.

## Assignment Requirements

### Problem Description

思源湖里全是鱼！作为资深捕鱼达人，我们需要捕捞更多的鱼。

假设湖由一个 `m x n` 的二维整数数组组成，如果某个格子的值是 `0`，则代表一块陆地格子；如果值大于 `0`，则代表一块水域格子，且鱼的数量就是该值；湖外全是陆地格子。捕鱼达人可以从任意水域格子出发，然后执行以下操作任意次：（1）捕捞格子中所有的鱼，（2）移动到相邻的水域格子。请返回捕鱼达人最优策略下，最多可以捕捞多少条鱼。如果没有水域格子，则返回 `0` 。

### Input Format

第一行输入两个数，代表湖的高 `m` 和宽 `n`。

第二行开始输入 `m` 行，每行 `n` 个数，代表该格子的数值。

### Output Format

最多能捕捞的鱼的数量。

### Samples

#### Sample 1

**Input:**
```
4 4
0 2 1 0
4 0 0 3
1 0 0 4
0 3 2 0
```

**Output:**
```
7
```

### Data Constraints

对于 100% 的数据，$m, n \leq 100$。

格子值的范围为 $[0, 9]$ 。

## Per-Testcase Resource Limits

- **Time Limit (per test case)**: 1000 ms
- **Memory Limit (per test case)**: 244 MiB
- **Disk Usage**: No disk usage is permitted.

## Test Data

The test data for this problem is located at `/workspace/data/099/data_test/`.

## Submission Requirements

### OJ Git Repository Compilation Process

For Git compilation, we will first clone the repository using a command similar to:
```bash
git clone <repo_url> . --depth 1 --recurse-submodules --shallow-submodules --no-local
```

Then we check if there is a `CMakeLists.txt` file. If it exists, we run (if not, a warning message will be displayed):
```bash
cmake .
```

Finally, we check if there is any of `GNUmakefile`/`makefile`/`Makefile` (if cmake was run previously, this will be the generated Makefile). If it exists, we run (if not, a warning message will be displayed):
```bash
make
```

After this process is complete, we will use the `code` file in the project root directory as the compilation result.

A `CMakeLists.txt` file is provided in the project. You can use or modify it as needed. The local environment has gcc-13 and g++-13 available.

### Git Configuration Requirements

**IMPORTANT**: You must create a `.gitignore` file in your project root directory to avoid OJ evaluation conflicts.

The `.gitignore` file should include at least the following entries:

```gitignore
CMakeFiles/
CMakeCache.txt
```

### Submission Guidelines

- The submitted code must be able to compile successfully through the above compilation process
- The compiled executable file name must be `code`
- The program needs to be able to read data from standard input and write results to standard output
- Please ensure the code runs correctly within the given time and space limits
- **You must use C++ or C language** to implement this assignment

### Evaluation Notes

- The evaluation system will test your program using the provided test data
- The program output must exactly match the expected output (including format)
- Exceeding time or memory limits will be judged as the corresponding error type
- Please pay attention to the overall time performance of your code and the time complexity of each part of your algorithm.

### Academic Integrity

If any violations are found during evaluation or code review (including but not limited to using unconventional methods to pass test cases), your final score may be significantly reduced or become **0 points**.
