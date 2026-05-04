#ifndef SRC_HPP
#define SRC_HPP
#include <iostream>

struct Permutation { // 置换
    int* mapping; // 我觉得这里存啥你应该知道
    size_t size; // 上面那个数组的长度

    Permutation(size_t size) {
        // TODO: 初始化一个长度为size的置换，内容为恒等置换。
    }

    Permutation(const int* mapping, size_t size) {
        // TODO: 初始化一个置换，内容为mapping，大小为size
    }

    ~Permutation() {
        // TODO: 析构函数，合理管理你的内存😈
    }

    void apply(int* permutation) const {
        // TODO：对于大小为size的数组permutation，将置换应用到它上，直接修改permutation指向的数组。
    }

    Permutation operator*(const Permutation& other) const {
        // TODO: 返回两个置换的乘积，即this*other。保证this和other的大小相同。
    }

    Permutation inverse() const {
        // TODO: 返回该置换的逆置换
    }

    friend std::ostream& operator<<(std::ostream& os, const Permutation& p) {
        // 这里重载了输出流，使得输出更方便。这里不需要修改代码。
        os << "[";
        for (size_t i = 0; i < p.size; ++i) {
            os << p.mapping[i];
            if (i < p.size - 1) {
                os << " ";
            }
        }
        os << "]";
        return os;
    }
};

struct Transposition { // 对换
    int a, b;

    Transposition() {
        // TODO: 初始化对换为恒等对换
    }

    Transposition(int a, int b)  {
        // TODO: 初始化对换为{a,b}
    }

    void apply(int* permutation, size_t size) const {
        // TODO: 将对换应用permutation上，直接修改permutation指向的数组。保证size>a且size>b。
    }

    friend std::ostream& operator<<(std::ostream& os, const Transposition& t) {
        // 这里重载了输出流，使得输出更方便。这里不需要修改代码。
        os << "{" << t.a << " " << t.b << "}";
        return os;
    }

    Permutation toPermutation(size_t size) const {
        // TODO: 将对换转换为大小为size的置换。保证size>a且size>b。返回一个置换。
    }
};

struct Cycle { // 轮换
    int* elements;// 我也觉得这里存啥你应该知道
    size_t size;

    Cycle(const int* elements, size_t size) {
        // TODO: 初始化一个轮换，内容为elements，大小为size
    }

    ~Cycle() {
        // TODO: 析构函数，合理管理你的内存😈
    }

    void apply(int* permutation, size_t size) const {
        // TODO: 将轮换应用大小为size的permutation上，直接修改permutation指向的数组。保证size>=elements[i]。
    }

    friend std::ostream& operator<<(std::ostream& os, const Cycle& c) {
        // 这里重载了输出流，使得输出更方便。这里不需要修改代码。
        os << "{";
        for (size_t i = 0; i < c.size; ++i) {
            os << c.elements[i];
            if (i < c.size - 1) {
                os << " ";
            }
        }
        os << "}";
        return os;
    }

    Permutation toPermutation(size_t size) const {
        // TODO: 将轮换转换为大小为size的置换。保证size>=elements[i]。返回一个置换。
    }
};


#endif