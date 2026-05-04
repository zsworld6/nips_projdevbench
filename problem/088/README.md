# Problem 088 - T3 魔术

**OJ Problem ID**: 2107

## Table of Contents

- [Problem 088 - T3 魔术](#problem-088-t3-魔术)
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
| Pass **2107. T3 魔术** | 80% |
| Code Review | 20% |

Here are several points that need clarification:

- In the Code Review, we will **strictly examine your code style and repository organization structure, etc.**

- This assignment provides some sample data for testing, stored in the `/workspace/data/088/data_test/` directory. Note that these are not the test cases on the Online Judge. Passing all local test cases does not guarantee that you will pass the OJ tests.

- Besides the provided sample data, we also encourage you to design your own test data based on your program logic to assist debugging.

## Assignment Requirements

### Problem Description

Conless 一早就知道今年的春晚很无聊，于是窝在房间里打游戏。但是不出意外地，他没多久就被家人拉到了电视机前，只好边打瞌睡边看春晚。到了魔术环节，昏昏欲睡的 Conless 终于打起了精神，想看看刘谦今年又有什么新把戏。很遗憾，由于注意力不够集中，关顾着看旁边嘉宾的乐子了，他没有发现其中的奥妙。

所以 Conless 只能寻求你们的帮助。问题简化如下：有 $n$ 张扑克牌，编号为 $1-n$，每一回合依次进行以下两个操作：
1. 「好运留下来」：把第一张牌放到当前排堆的最后
2. 「烦恼丢出去」：丢弃上一步操作后当前排堆的第一张牌

问在进行若干次这样的操作后，牌堆中留下的最后一张牌编号是多少？

本题有两个子任务点：
- Subtask 1. 模拟魔术的过程：该任务点要求你 **手动实现** 一个链表模拟牌堆，并输出每一回合结束后牌堆的情况，共 $n-1$ 回合；输出格式见下。
- Subtask 2. 预测魔术的结果：该任务点希望你 **直接** 预测魔术的结果，即输出对于给定的 $n$，牌堆中留下的最后一张牌的编号。

对于 Subtask 2，如果没有思路或者遇到了 TLE 的问题，下方数据点范围可能会给予你一些提示。

### Input Format

两个整数 $id$ 和 $n$，分别表示子任务点的编号和牌堆中牌的数量。

### Output Format

对于 Subtask 1，输出 $n-1$ 行，第 $i$ 行一个整数 $top_i$，表示第 $i$ 回合结束后牌堆中的第一张牌的编号。

对于 Subtask 2，输出一个整数，表示牌堆中留下的最后一张牌的编号。

### Samples

No sample data provided for this problem.

### Data Constraints

<table border="1" cellpadding="1" cellspacing="1">
	<thead>
		<tr>
			<th scope="col" style="text-align:center">测试点</th>
			<th scope="col" style="text-align:center">Subtask ID</th>
			<th scope="col" style="text-align:center">n</th>
      <th scope="col" style="text-align:center">进行内存泄漏检查</th>
		</tr>
	</thead>
	<tbody>
		<tr>
      <td style="text-align:center"> 1 </td>
      <td rowspan="7" style="text-align:center"> 1 </td>
      <td rowspan="4" style="text-align:center"> &le; 100 </td>
      <td rowspan="4" style="text-align:center"> 是 </td>
    </tr>
    <tr>
      <td style="text-align:center"> 2  </td>
    </tr>
    <tr>
      <td style="text-align:center"> 3  </td>
    </tr>
    <tr>
      <td style="text-align:center"> 4  </td>
    </tr>
    <tr>
      <td style="text-align:center"> 5  </td>
      <td rowspan="3" style="text-align:center"> &le; 10<sup>5</sup> </td>
      <td rowspan="6" style="text-align:center"> 否 </td>
    </tr>
    <tr>
      <td style="text-align:center"> 6  </td>
    </tr>
    <tr>
      <td style="text-align:center"> 7 </td>
    </tr>
    <tr>
      <td style="text-align:center"> 8 </td>
      <td rowspan="3" style="text-align:center"> 2 </td>
      <td style="text-align:center"> &le; 10<sup>15</sup>, 且为 2 的整数次幂 </td>
    </tr>
    <tr>
      <td style="text-align:center"> 9 </td>
      <td rowspan="2" style="text-align:center"> &le; 10<sup>15</sup> </td>
    </tr>
    <tr>
      <td style="text-align:center"> 10 </td>
    </tr>
</tbody>
</table>

### 注意事项

在 Subtask 1 中，可能有别的实现方式，但是请你**自己实现一个链表**来模拟魔术操作（不可使用 `std::list`），助教将会人工检查你的代码并将不合法代码作废；在实现过程中，你需要**注意内存安全问题**，我们将在部分测试点中使用 `valgrind` 进行内存泄漏检查。

## Per-Testcase Resource Limits

- **Time Limit (per test case)**: 5000 ms
- **Memory Limit (per test case)**: 256 MiB
- **Disk Usage**: No disk usage is permitted.

## Test Data

The test data for this problem is located at `/workspace/data/088/data_test/`.

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
