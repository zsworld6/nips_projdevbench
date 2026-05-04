# Problem 083 - T3 约瑟夫环

**OJ Problem ID**: 1782

## Table of Contents

- [Problem 083 - T3 约瑟夫环](#problem-083-t3-约瑟夫环)
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
| Pass **1782. T3 约瑟夫环** | 80% |
| Code Review | 20% |

Here are several points that need clarification:

- In the Code Review, we will **strictly examine your code style and repository organization structure, etc.**

- This assignment provides some sample data for testing, stored in the `/workspace/data/083/data_test/` directory. Note that these are not the test cases on the Online Judge. Passing all local test cases does not guarantee that you will pass the OJ tests.

- Besides the provided sample data, we also encourage you to design your own test data based on your program logic to assist debugging.

## Assignment Requirements

### Problem Description

在算法竞赛中，约瑟夫环问题是一个经典问题。这个问题的描述如下：

给定 $n,m$ 。$1,\dots,n$ 这 $n$ 个数字排成一个圆，从数字 $1$ 开始，每次从圆圈中删除第 $m$ 个数字，删除后从下一个数字开始计数，则最后剩下的数字是哪个？

例如，对于 $n=5,m=3$ 的情形，删除的前 $4$ 个数字分别是 $3,1,5,2$ ，最后剩下的数字是 $4$ 。

这个问题有很多种解法，但为了考察同学们的工程能力，助教决定让大家使用单循环链表模拟的形式完成这道题目。**助教将手动检查每位同学的代码，其他解决方法（包括双循环链表）不能在本题中得到分数。**

单循环链表是一种特殊的单链表。在单循环链表中，链表的最后一个节点指向链表的第一个节点，构成了一个圆。单循环链表的结构如下：

![单循环链表](https://media.geeksforgeeks.org/wp-content/uploads/CircularLinkeList.png "单循环链表")

请**手动**构建（禁止使用 STL 以及任何其他外部库）一个有 $n$ 个元素的单循环链表，从 $1$ 号节点开始模拟计数的过程，每次将第 $m$ 个数字从单循环链表中删除，并输出其编号。最后输出剩余的最后一个元素。

本题有内存泄漏检查。

### Input Format

一行两个正整数 $n,m$。

### Output Format

$n$ 行，每一行按顺序输出一个被删除的数字。

### Samples

#### Sample 1

**Input:**
```
5 3
```

**Output:**
```
3
1
5
2
4
```

### Data Constraints

$1\leq m\leq n\leq 3000$

对于 $50\\%$ 的数据，有内存泄漏检查。

## Per-Testcase Resource Limits

- **Time Limit (per test case)**: 10000 ms
- **Memory Limit (per test case)**: 512 MiB
- **Disk Usage**: No disk usage is permitted.

## Test Data

The test data for this problem is located at `/workspace/data/083/data_test/`.

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
