#include "src.hpp"
#include <bits/stdc++.h>
#include <cassert>
#include <iostream>
int main() {
  Grammar::RegexChecker checker("abb*b?|abb+a");
  std::string test[4];
  test[0] = "abbb";
  test[1] = "aabbb";
  test[2] = "abba";
  test[3] = "ba";
  for(auto str : test) {
    if (checker.Check(str)) {
      std::cout << str << " Accepted." << std::endl;
    } else {
      std::cout << str << " Not Accepted." << std::endl;
    }
  }
  checker = Grammar::RegexChecker("a?b?a?ba*|abbb|baa");
  for(auto str : test) {
    if (checker.Check(str)) {
      std::cout << str << " Accepted." << std::endl;
    } else {
      std::cout << str << " Not Accepted." << std::endl;
    }
  }
  return 0;
}