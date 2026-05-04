# Problem 102 - 任意进制固定宽度字符串加法

**OJ Problem ID**: 2878

## Table of Contents

- [Problem 102 - 任意进制固定宽度字符串加法](#problem-102-任意进制固定宽度字符串加法)
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
| Pass **2878. 任意进制固定宽度字符串加法** | 80% |
| Code Review | 20% |

Here are several points that need clarification:

- In the Code Review, we will **strictly examine your code style and repository organization structure, etc.**

- This assignment provides some sample data for testing, stored in the `/workspace/data/102/data_test/` directory. Note that these are not the test cases on the Online Judge. Passing all local test cases does not guarantee that you will pass the OJ tests.

- Besides the provided sample data, we also encourage you to design your own test data based on your program logic to assist debugging.

## Assignment Requirements

### Problem Description

给定两个用字符数组表示的非负整数串 `str1` 与 `str2`，以及一个进制 `B`（2 ≤ B ≤ 36）。请计算它们的“和”，并以**固定宽度**（等于两串中较长者的位数）输出结果字符串。  
若最高位产生进位，则**按模截断**（在固定宽度内输出，丢弃超出位宽的进位）。数字字符约定：`0-9` 表示 0–9，`A-Z`/`a-z` 表示 10–35（大小写等价，输出一律使用大写）。

* 示例 1：`str1 = "123"`, `str2 = "456"`, `B = 10` → 输出 `579`。  
* 示例 2：`str1 = "1"`, `str2 = "99"`, `B = 10`；较长位数为 2，`1 + 99 = 100`，固定 2 位 → 输出 `00`（最高位进位被截断）。  
* 示例 3：`str1 = "0f"`, `str2 = "1"`, `B = 16`；较长位数为 2 → 输出 `10`。

* 题目描述特殊说明 1：所有输入字符串均为以 `'\0'` 结尾的 C 字符串，输入给出的长度 `m`、`n` **包含** 终止符。  
* 题目描述特殊说明 2：输出为长度恰为 `max(m-1, n-1)` 的大写字符串（不包含空格与多余字符）。

### Input Format

第一行输入三个整数 $m$ $n$ $B$（空格分隔），$m$、$n$ 分别为 `str1` 与 `str2` 的总长度（**包含** 终止符 `'\0'`），保证 $m > 1$, $n > 1$，并且 $2 ≤ B ≤ 36$。  
第二行输入字符串 `str1`（长度为 $m-1$）。  
第三行输入字符串 `str2`（长度为 $n-1$）。

* 输入特殊说明：输入字符串仅包含 `0-9`、`A-Z`、`a-z`，不含符号与空白。

### Output Format

输出一行：长度为 $\max(m-1, n-1)$ 的**大写**结果字符串。

* 输出特殊说明：若发生最高位进位，只保留固定宽度内的部分（按模截断），不足位用前导零补齐。

### Samples

#### 样例 1

**Input:**
```
4 4 10
123
456
```

**Output:**
```
579
```

#### 样例 2

**Input:**
```
2 3 10
1
99
```

**Output:**
```
00
```

#### 样例 3

**Input:**
```
3 2 16
0f
1
```

**Output:**
```
10
```

### Data Constraints

* 有效位数 $< 600$（即 $m-1 < 600$ 且 $n-1 < 600$）。  
* 时间限制：2000 ms。（OJ 运维注：请以下方显示的时间、内存限制为准。）  
* 内存限制：256 MiB。

## Per-Testcase Resource Limits

- **Time Limit (per test case)**: 2000 ms
- **Memory Limit (per test case)**: 256 MiB
- **Disk Usage**: No disk usage is permitted.

## Test Data

The test data for this problem is located at `/workspace/data/102/data_test/`.

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
