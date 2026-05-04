# Problem 078 - 小恶魔的类

**OJ Problem ID**: 1444

## Table of Contents

- [Problem 078 - 小恶魔的类](#problem-078-小恶魔的类)
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
| Pass **1444. 小恶魔的类** | 80% |
| Code Review | 20% |

Here are several points that need clarification:

- In the Code Review, we will **strictly examine your code style and repository organization structure, etc.**

- This assignment provides some sample data for testing, stored in the `/workspace/data/078/data_test/` directory. Note that these are not the test cases on the Online Judge. Passing all local test cases does not guarantee that you will pass the OJ tests.

- Besides the provided sample data, we also encourage you to design your own test data based on your program logic to assist debugging.

## Assignment Requirements

### Problem Description

助教是个小恶魔，但她最后还是决定放大家一马，于是她决定让大家写个 $Evil$ 类。

 $Evil$ 类内存储一个小恶魔的所有信息，类中元素包括：

-  $st$ 和 $ed$ 。表示小恶魔在第 $st$ 天到第 $ed$ 天出现；
- 数组 $data[]$ 。存储小恶魔的能量值，第 $i(st \leq i \leq ed)$ 天的能量值为 $data[i]$ ；
-  $val$ 。表示小恶魔的邪恶指数，由于某些原因，小恶魔的邪恶指数 $val$ 只增不减。

你需要实现以下函数：

-  $Evil$ 类中的构造函数
   -  默认 $st$ , $ed$ , $val$ 均为 $0$ ， $data[]$ 初值均为 $0$

-  $Evil$ 类中的下标运算符重载 `operator []`
   -  输入 $data[i]$, 返回保存第 $i$ 天的能量值的变量
   -  若 $i$ 不满足 $\mathbf {st \le i \le ed}$ ，返回第 $st$ 天的能量值

-  $Evil$ 类中的赋值运算符重载 `operator =​` 

-  $Evil$ 类中前置++和后置++的重载
   -  每次类中的 $val$ 加 $1$ 

-  $Evil$ 类中的输出运算符重载 `operator <<` 
   -  每次输出一行，共 $ed-st+2$ 个数，其中第一个值为 $val$，接着输出 $st$ 天到 $ed$ 天的能量值 $data[]$
   -  数字用空格隔开，结尾输出换行符

-  $Evil$ 类中的析构函数


**特别注意：**

 - **不能在类中定义新的成员变量，不能修改成员变量的类型（如将 `private` 类型修改为 `public` 类型），不能修改类中已经给定的函数，可以新增加函数。**

 - **如果未实现输出运算符重载，可以通过类中的 `Print()` 函数达到同样效果。**

 - **数据保证都在 `int` 范围内，即不需要也不能更改成员变量的类型。**

 - **无论测试哪个数据点，都会调用构造函数，请大家务必要写构造函数。**

 - **程序最终会检查内存泄漏问题，若出现内存泄漏，则得分为原来的80%。** 

```c++
#ifndef EVIL_HPP
#define EVIL_HPP

#include <iostream>
using namespace std;

class Evil{
private:
	int st, ed, val;
	int *data;

public:
    
//构造函数
//下标运算符重载
//赋值运算符重载
//前缀++重载
//后缀++重载
//输出重载
//析构函数

    void Print(){
	    cout << val << " ";
	    for(int i = 0;i < ed-st+1;++i)
	        cout << data[i] <<" ";
	    cout << endl;
	}
};

#endif//EVIL_HPP	
```
main.cpp:
```c++
#include <bits/stdc++.h>
#include "evil.hpp"
using namespace std;

int main(){
	int T;
	cin >> T ;
	while (T--) {
		int type;
		cin >> type;

		int test_0_st, test_0_ed, test_0_val;
		cin >> test_0_st >> test_0_ed >> test_0_val;
		Evil test_0_0(test_0_st, test_0_ed, test_0_val);

		if (type == 0){
			test_0_0.Print();
			Evil test_0_1;
			test_0_1.Print();
		}
		if(type == 1){
			Evil test_1_1;
			test_1_1 = test_0_0;
			test_1_1.Print(); 
		}
		if(type == 2){
			for(int i = test_0_st;i <= test_0_ed;++i) test_0_0[i] = i;
			test_0_0[test_0_st-1] = test_0_st-1;
			cout << test_0_0[test_0_st-1] << " " << test_0_0[test_0_ed+1] <<" ";
			test_0_0.Print();
		}
		if(type == 3){
		    test_0_0++;
		    test_0_0++;
			test_0_0.Print();
			
			++test_0_0; ++test_0_0;
			test_0_0.Print();
		}
		if(type == 4){
			cout << test_0_0;
		}
	}
	return 0;
}
```

### Input Format

第一行有一个整数 $T$，表示数据组数。

之后有 $T$ 行，每行的第一个整数 $type$ 表示测试类型，第 $2-4$ 个数表示初始的 $Evil$ 类中 $st$ , $ed$ , $val$ 。

 $type=0$ 时，测试构造函数。

 $type=1$ 时，测试赋值运算符的重载。

 $type=2$ 时，测试下标运算符的重载。

 $type=3$ 时，测试前缀++和后缀++的重载

 $type=4$ 时，测试输出运算符的重载

保证一个测试文件中的 $type$ 都相等。

### Output Format

具体输出格式请看主函数。

### Samples

#### Sample 1

**Input:**
```
5
0 1 10 3
1 2 5 6
2 3 6 8
3 4 9 8
4 2 9 10
```

**Output:**
```
3 0 0 0 0 0 0 0 0 0 0 
0 0 
6 0 0 0 0 
2 2 8 2 4 5 6 
10 0 0 0 0 0 0 
12 0 0 0 0 0 0 
10 0 0 0 0 0 0 0 0 
```

### Data Constraints

| 测试点编号 |  $type$   | Hint| 分值 |
| ------- | ----- | -----| ----|
|  $1$  | 0      | 测试构造函数 | 10% |
|  $2$     | 1      | 测试赋值运算符的重载 | 10% |
|  $3-5$  | 2      | 测试下标运算符的重载​ | 30%|
|  $6-7$  | 3      | 测试前缀++和后缀++重载 | 20% |
|  $8-10$  | 4 | 测试输出运算符重载 | 30% |

## Per-Testcase Resource Limits

- **Time Limit (per test case)**: 2000 ms
- **Memory Limit (per test case)**: 256 MiB
- **Disk Usage**: No disk usage is permitted.

## Test Data

The test data for this problem is located at `/workspace/data/078/data_test/`.

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
