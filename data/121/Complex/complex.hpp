#ifndef SJTU_COMPLEX_HPP
#define SJTU_COMPLEX_HPP

#include <iostream> // 输入输出
#include <iomanip>  // 控制输出格式
#include <cmath>    // 数学函数
#include <stdexcept> // 异常处理
// 你不可以使用任何其他的头文件!


namespace sjtu {

// 异常类，你需要要添加一个函数 what() 来返回异常信息。
class divided_by_zero final : public std::exception {
  public:
    divided_by_zero()   = default;
    ~divided_by_zero()  = default;
    // TODO
};

// 用于判断浮点数的符号.
inline int sign(double x) {
    const double eps = 1e-6;
    return (x > eps) - (x < -eps);
}

// 请保留所有的接口声明，即使你没有实现它们。
// 否则可能出现编译错误，无法通过部分测试点。
// TODO 补全类的实现
class complex {
  private:
    double a, b; // a + bi
  public:
    
    complex();                    // 默认构造函数 0+0i
    complex(double a);            // 构造函数 a+0i
    complex(double a, double b);  // 构造函数 a+bi

    double &real(); // 返回实部
    double &imag(); // 返回虚部

    complex operator - () const; // 返回负数
    complex operator ~ () const; // 返回共轭复数

    complex operator + (const complex &rhs) const; // 加法
    complex operator - (const complex &rhs) const; // 减法
    complex operator * (const complex &rhs) const; // 乘法
    complex operator / (const complex &rhs) const; // 除法

    complex &operator += (const complex &rhs);
    complex &operator -= (const complex &rhs);
    complex &operator *= (const complex &rhs);
    complex &operator /= (const complex &rhs);

    bool operator == (const complex &rhs) const; // 判断相等
    
    explicit operator bool() const; // 转换为 bool

    friend std::ostream &operator << (std::ostream &os, const complex &x); // 输出
};

}

#endif