# Problem 037 - 双链表，启动！

**OJ Problem ID**: 2600

## Table of Contents

- [Problem 037 - 双链表，启动！](#problem-037-双链表启动)
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

Implement doubly linked list with insert, query, delete, print operations.

## Assignment Description

### Grade Composition

| Grading Component | Percentage |
| :--: | :--: |
| Pass **2600. 双链表，启动！** | 80% |
| Code Review | 20% |

Here are several points that need clarification:

- In the Code Review, we will **strictly examine your code style and repository organization structure, etc.**

- This assignment provides some sample data for testing, stored in the `/workspace/data/037/data_test/` directory. Note that these are not the test cases on the Online Judge. Passing all local test cases does not guarantee that you will pass the OJ tests.

- Besides the provided sample data, we also encourage you to design your own test data based on your program logic to assist debugging.

## Assignment Requirements

### Problem Description

请你按照课堂所学，实现一个双链表，你需要实现以下函数功能（下列i都从0计数）：
* 操作0：长度统计```int Get_length()```。
* 操作1：在位置i插入一个数```void insert(int i, int x)```，注意这里是指插入的数在插入后处于位置i，即插入在现在位置i数字的前面。
* 操作2：返回第x个数```int Query(int i)```，如果x超出链表长度，请输出-1。
* 操作3：删除位置i的数```void remove(int i)```，整个链表长度--。
* 操作4：输出整个list```void Print()```，如果表为空请输出-1。
* 最后，为防止内存泄漏，你需要在程序最后删除整个列表，实现```void Clear()```函数
  
具体来说，你需要补全以下代码的//TODO部分，实现上述所说的六个函数。

```c++
#include <bits/stdc++.h>
#include <iostream>
using namespace std;

namespace DoubleLinkList {

struct NODE {
    int data;
    NODE *next;
    NODE *pre;
    NODE() {}
    NODE(int val) { this->data = val; }
};

NODE *head = nullptr, *tail = nullptr;
int len = 0;

void Pre() {
    head = new NODE();
    tail = new NODE();
    head->pre = NULL;
    tail->next = NULL;
    head->next = tail;
    tail->pre = head;
}
NODE *move(int i) {
    NODE *cur = head;
    for (int j = 0; j <= i; j++) {
        cur = cur->next;
    }
    return cur;
}
void insert(int i, int x) {
    //TODO
}
void remove(int i) {
    //TODO
}
int Get_length() {
    // TODO
    
}
int Query(int i) {
    // TODO
    
}

void Print() {
    // TODO
}

void Clear() {
    // TODO
}

} // namespace DoubleLinkList
int n;
int main() {
    cin >> n;
    int op, x, p, ans;
    DoubleLinkList::Pre();
    for (int _ = 0; _ < n; ++_) {
        cin >> op;
        switch (op) {
        case 0:
            ans = DoubleLinkList::Get_length();
            cout << ans << endl;
            break;
        case 1:
            cin >> p >> x;
            DoubleLinkList::insert(p, x);
            break;
        case 2:
            cin >> p;
            ans = DoubleLinkList::Query(p);
            cout << ans << endl;
            break;
        case 3:
            cin >> p;
            DoubleLinkList::remove(p);
            break;
        case 4:
            DoubleLinkList::Print();
            break;
        }
    }
    DoubleLinkList::Clear();
    return 0;
}

```
（题目改编于4296，进一步降低难度，希望帮助大家熟悉双链表^_^）

### Input Format

第一行一个 $n$ 表示操作数

之后 $n$ 行每行第一个数 $op$ 代表操作编号，分别对应前文中的编号。

如果 $op$ 为 $1$，其后会输入两个整数 $p,x$，表示在 $p$ 位置插入的数值为 $x$。

如果 $op$ 为 $2$，其后会输入一个整数 $p$，表示你需要输出链表中 $p$ 位置的值，输出要求见下。

(数据保证插入删除操作不会操作无效位置。)

### Output Format

对于操作1,3，你不用输出任何东西。

对于操作0，输出一个整数，表示链表长度。

对于操作2，输出一个整数，表示第x个数。

对于操作4，按链表顺序输出一行整数。

### Samples

#### Sample 1

**Input:**
```
3
0
1 0 1
0
```

**Output:**
```
0
1
```

### Data Constraints

See the problem description for constraints.

## Per-Testcase Resource Limits

- **Time Limit (per test case)**: 1000 ms
- **Memory Limit (per test case)**: 256 MiB
- **Disk Usage**: No disk usage is permitted.

## Test Data

The test data for this problem is located at `/workspace/data/037/data_test/`.

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
