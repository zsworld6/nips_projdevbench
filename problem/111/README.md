# Problem 111 - Cstring Implement III

**OJ Problem ID**: 1351

## Table of Contents

- [Problem 111 - Cstring Implement III](#problem-111-cstring-implement-iii)
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
    - [Submission Format](#submission-format)
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
| Pass **1351. Cstring Implement III** | 80% |
| Code Review | 20% |

Here are several points that need clarification:

- In the Code Review, we will **strictly examine your code style and repository organization structure, etc.**

- This assignment provides some sample data for testing, stored in the `/workspace/data/111/data_test/` directory. Note that these are not the test cases on the Online Judge. Passing all local test cases does not guarantee that you will pass the OJ tests.

- Besides the provided sample data, we also encourage you to design your own test data based on your program logic to assist debugging.

## Assignment Requirements

### Problem Description

这是一道头文件题目。你要实现给定的一个函数，并把头文件提交到OJ上。在头文件中不允许使用**任何**标准库，也不允许使用**任何**全局变量。

本题的下发文件可以从 ~~[SJTU JBOX](https://jbox.sjtu.edu.cn/l/y1nnIf)~~ [attachment]1351-handout.zip[/attachment] 下载。<a href="https://wwqd.lanzoul.com/i0JjR1ikojjc">备用下载地址</a>。`src.hpp` 为你需要实现的头文件；`main.cpp` 为评测所用的主程序。

在本题中，你需要实现 `strtok` 一个函数，该函数严格等同于标准库中的 `std::strtok` 函数。它的定义如下：

```C++
/**
 * @brief split STRing by TOKen：以delim为分隔符，分隔字符串str。
 * @param str 源字符串
 * @param delim 一个字符串，其中每一个字符都被当成一种分隔符
 * @return 返回分割得到的第一个字符串。
 * @par 具体来说，strtok会找到字符串中delim中字符第一次出现的位置，
 *      然后把这个位置的字符修改为'\0'，然后返回原字符串。
 *      为了支持多次分隔，可以在str参数中传入空指针，
 *      那么函数的返回值是上一次调用的“原串”以delim分隔得到的第二部分，
 *      若再次调用则为第三部分，以此类推。
 */
char *strtok( char * __restrict str, const char * __restrict delim );
```

阅读文档对于标准库函数的使用是极其重要的。请查阅下面的链接，获得strtok的严谨定义。

请参考 <https://zh.cppreference.com/w/c/string/byte/strtok> 中 1）的全部内容。
（P.S. 助教在出这道题的时候甚至还修了 cppreference 上的一个错误）

为了便于理解这个函数，我们介绍一下 `strtok` 函数的典型使用方式：

```C++
//output:
//text abc 
// def 
// ghi
int main () {
    char str[] = "text abc - def - ghi";
    const char s[] = "-";
    char *token = nullptr;

    /* 获取第一个子字符串 */
    token = strtok(str, s);

    /* 继续获取其他的子字符串 */
    while(token != nullptr) {
        std::cout << token << std::endl;
        token = strtok(nullptr, s);
    }

    return 0;
}

```

`strtok` 的缺点是会破坏原串。因此，使用它的时候请确保原串不会在调用后被再次用到；或者，也可以复制一个新串作为 `strtok` 的参数。

另外，为了实现传入 `nullptr` 多次分隔的特性，你可能会需要一些函数内的静态变量。

不需要考虑 `str` 和 `delim` 有重叠的情况。

### Input Format

第一行输入 $n$，表示操作数

接下来 $n$ 行，每行一个操作。操作形如：

- `1 s1 s2` 表示需要做一次 `strtok(s1, s2)` 和多次 `strtok(nullptr, s2)`，直至把字符串分割完成。

### Output Format

评测程序会输出函数的返回值。

`strtok` 可能会有多次调用，我们会每行输出一个返回值。

### Samples

#### Sample 1

**Input:**
```
2
1 abcdefaedd abd
1 textabcwdefwghi w
```

**Output:**
```
c
ef
e
textabc
def
ghi
```

### Data Constraints

所有的字符串都是小写英文字母构成的。

保证输入的字符串总长度小于等于 $10^6$。

## Resource Limits

- **Time Limit**: 1000 ms
- **Memory Limit**: 256 MiB

## Per-Testcase Resource Limits

- **Time Limit (per test case)**: 1000 ms
- **Memory Limit (per test case)**: 256 MiB
- **Disk Usage**: No disk usage is permitted.

## Test Data

The test data for this problem is located at `/workspace/data/111/data_test/`.

Attachments and starter files for this problem are located at `/workspace/data/111/`.

## Submission Requirements

### Submission Format

Submit a single C++ source file to the Online Judge. The OJ provides its own `main.cpp` which `#include "src.hpp"`. Your submission will be written to `src.hpp` and compiled together with the OJ's driver code.

### Submission Guidelines

- The submitted code must be able to compile successfully through the above compilation process
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
