# Problem 044 - 小可怜的字符串

**OJ Problem ID**: 14297

## Table of Contents

- [Problem 044 - 小可怜的字符串](#problem-044-小可怜的字符串)
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

Implement mystring class with constructors, operator overloading (<, ==), concatenation (+, +=), substr, insert, erase.

## Assignment Description

### Grade Composition

| Grading Component | Percentage |
| :--: | :--: |
| Pass **14297. 小可怜的字符串** | 80% |
| Code Review | 20% |

Here are several points that need clarification:

- In the Code Review, we will **strictly examine your code style and repository organization structure, etc.**

- This assignment provides some sample data for testing, stored in the `/workspace/data/044/data_test/` directory. Note that these are not the test cases on the Online Judge. Passing all local test cases does not guarantee that you will pass the OJ tests.

- Besides the provided sample data, we also encourage you to design your own test data based on your program logic to assist debugging.

## Assignment Requirements

### Problem Description

author: 小可怜
原OJ链接：https://acm.sjtu.edu.cn/OnlineJudge-old/problem/4297
# 小可怜的字符串

## Description
助教是个小可怜，因为她不知道要出什么机考题了。
然后她发现，大家终于可以面向对象变成了。
啊！面向对象！
于是她想让大家写个mystring~ 
你需要完成以下内容：（注意这里的i都为**0-base**）
- 构造一个长度为len以某个字符初始化的mystring。
  
- 从string中构造一个mystring。(请注意，mystring中char数组长度应和传入的string长度保持一致。可调用`c.length()`获得传入字符串的长度)。
  
- 用下标输出mystring变量中的第x位(若x超过字符串长度输出'\0').
  
- 重载运算符<, 比较两个mystring类型字符串的大小.(比较方式：先比较每一位上字符，再比较长度。例:aaaa<b)
  
- 写一个ADD函数，将一个mystring类型字符串接到另一个之后。
  
- 写一个out函数（你也可以重载输出运算符）输出mystring类型字符串。（使用重载运算符即是采用主程序注释中的输出方式，主程序仅允许此种情况的修改。）
  
- 写一个get_len函数，输出mystring类型中储存的字符串长度。
  
- 为防止内存泄漏，写一个析构函数。


要求如下：

- 不得修改超出要求允许的部分。
- 如未按要求完成，对应测试点不得分。
- 请严格按照以上要求完成此题。我们会检查你提交的代码。虽然有其他的实现方式，但如果你未按照要求写代码，我们**不会**给你分数。
- 同时，**此题需要你注意提交代码的代码风格！！！极为糟糕的代码风格（例如改变语法的某些宏定义）会酌情扣分！！！**

### Input Format

第一行一个$id$表示操作号。
其余输入具体见给定代码的主程序部分。

### Output Format

输出方式详见主程序。
你的out函数中不需要进行换行。

## SAMPLE INPUT

    0
    aabbcc abcdef
    3
    0
    3
    5

## SAMPLE OUTPUT

    a
    d
    f
    6 6
    1
    aabbccabcdef


## DATA LIMIT

保证所有字符串长度$1 \leq len \leq 200$.

## Hint

测试点编号 | id|  
-|-|
1 | 1 |
2 | 2 |
3 | 3 |
4 | 4 |
5 | 0 |

每个测试点20分，如果对应操作未按要求完成，哪怕通过对应测试点，对应测试点也不得分。
（比如重载<的操作未按要求完成，3、5测试点不得分。）
（同样，如果检查代码发现未按要求处理内存泄漏，得分砍半指若你在此题得分80，最后只计得分40.）


**本题只有一次提交机会！！！**

`sample.cpp`如下


    #include <string>
    #include <cstring>
    #include <iostream>
    #include <cstdio>
    #include <cstdlib>
    using namespace std;
    
    class mystring
    {
    private:
        char *ch = nullptr;
        int len = 0;
    
    public:
    
        mystring()
        {
            // TODO
        }
        mystring(int _len, int c)
        {
            // TODO
        }
        mystring(string &c)
        {
            // TODO
        }
        ~mystring()
        {
            // TODO
        }
    
        // TODO
    };
    
    string str_in1, str_in2;
    int n, id;
    int main()
    {
        cin >> id;
        if (id == 1)
        {
            mystring str1(100,'a');
            str1.out(); puts("");
            // cout << str1 << endl;
        }
        else if (id == 2)
        {
            cin >> str_in1;
            mystring str2 = str_in1;
            cin >> n;
            for (int i = 0, x; i < n; ++ i)
            {
                cin >> x;
                cout << str2[x] << endl;
            }
        }
        else if (id == 3)
        {
            cin >> str_in1 >> str_in2;
            mystring str2 = str_in1;
            mystring str3 = str_in2;
            cout << (int)(str2 < str3) << endl;
        }
        else if (id == 4)
        {
            cin >> str_in1 >> str_in2;
            mystring str2 = str_in1;
            mystring str3 = str_in2;
            str2.ADD(str3);
            str2.out(); puts("");
            // cout << str2 << endl;
        }
        else
        {
            cin >> str_in1 >> str_in2;
            mystring str2 = str_in1;
            mystring str3 = str_in2;
            cin >> n;
            for (int i = 0, x; i < n; ++ i)
            {
                cin >> x;
                cout << str3[x] << endl;
            }
            cout << str2.get_len() << " " << str3.get_len() << endl;
            cout << (int)(str2 < str3) << endl;
            str2.ADD(str3);
            str2.out(); puts("");
            // cout << str2 << endl;
            cout << str2.get_len() << endl;
        }
        return 0;
    }


See the problem description above.


See the problem description above.

### Samples

No sample data provided for this problem.

### Data Constraints

See the problem description for constraints.

## Per-Testcase Resource Limits

- **Time Limit (per test case)**: 2000 ms
- **Memory Limit (per test case)**: 1024 MiB
- **Disk Usage**: No disk usage is permitted.

## Test Data

The test data for this problem is located at `/workspace/data/044/data_test/`.

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
