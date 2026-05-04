//
// Created by wzj on 2021/12/3.
// Modified by Yifei Ma on 2023/10/25.
//

#ifndef FINAL_SRC_HPP
#define FINAL_SRC_HPP

#include <string>
#include <vector>

// If the two following commands bother you, you may comment them and write
// std::vector and std::string instead.
using std::string;
using std::vector;

struct LinkedHashMap;
struct Node {
  Node* next = nullptr;
  Node* timePre = nullptr;
  Node* timeNext = nullptr;

  int key = 0;
  string value;
};

struct Data {
  int key;
  string value;
};

vector<Data> traverseByTime(const LinkedHashMap& obj);
vector<Data> traverseByIndex(const LinkedHashMap& obj);

struct LinkedHashMap {
  // You can modify beg, cur and related parts in the constructor as you wish.
  // 你可以根据自己写链表的习惯修改或删除头尾节点并修改构造函数。

  int len;
  Node** array;
  Node* beg;
  Node* cur;
  // TODO: define a function pointer named "forEachMethod"
  // to be pointed to one of the functions "traverseByTime" or "traverseByDict".
  // 定义一个名为 forEachMethod 的函数指针，用于指向 travelByTime 或
  // travelByDict 函数。

  void init(int len_, bool forEachByTime) {
    len = len_;
    beg = new Node();
    cur = beg;
    array = new Node*[len];
    for (int i = 0; i < len; i++) {
      array[i] = nullptr;
    }
    if (forEachByTime)
      forEachMethod = traverseByTime;
    else
      forEachMethod = traverseByIndex;
  }

  void clearMemory() {
    // TODO
  }

  void insert(int key, string value) {
    // TODO
  }

  void remove(int key, string value) {
    // TODO
  }

  vector<string> ask(int key) const {
    // TODO
  }

  vector<Data> forEach() const { return forEachMethod(*this); }
};

vector<Data> traverseByTime(const LinkedHashMap& obj) {
  // TODO
}

vector<Data> traverseByIndex(const LinkedHashMap& obj) {
  // TODO
}

#endif  // FINAL_SRC_HPP
