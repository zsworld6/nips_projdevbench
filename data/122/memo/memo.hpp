#ifndef MEMO_HPP
#define MEMO_HPP

#include "event.h"

inline std::string CustomNotifyLateEvent::GetNotification(int n) const {
  // TODO(student): Implement this function
  // Implementation detail of this function is in event.h
}

class Memo {
 public:
  // 显示删除默认构造函数
  Memo() = delete;

  // 构造函数，参数duration表示需要模拟第1~duration小时的备忘录
  Memo(int duration) {
    // TODO(student): Implement this function
  }

  // 析构函数，需保证没有内存泄漏
  ~Memo() {
    // TODO(student): Implement this function
  }

  // 向备忘录中加入一项事件。传入一个Event指针，需根据实际派生类类型进行具体操作
  void AddEvent(const Event *event) {
    // TODO(student): Implement this function
  }

  // 模拟时间流逝，进行下一个小时的事件提醒
  void Tick() {
    // TODO(student): Implement this function
  }

 private:
   // TODO(student): Add your variables/functions here
};
#endif