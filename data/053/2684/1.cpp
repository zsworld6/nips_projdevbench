#include "src.hpp"
#include <bits/stdc++.h>
#include <iostream>
#include <unordered_set>
int main() {
  auto nfa = Grammar::MakeSimple('a');
  std::unordered_set<int> current_states;
  current_states.insert(nfa.GetStart());
  for (int i = 0; i < 10; i++) {
    current_states = nfa.Advance(current_states, 'a');
    bool flag = false;
    for (const auto &state : current_states) {
      if (nfa.IsAccepted(state)) {
        std::cout << "Accepted." << std::endl;
        flag = true;
      }
      break;
    }
    if (!flag) {
      std::cout << "Not Accepted." << std::endl;
    }
  }
  current_states.clear();
  current_states.insert(nfa.GetStart());
  for (int i = 0; i < 10; i++) {
    current_states = nfa.Advance(current_states, 'b');
    bool flag = false;
    for (const auto &state : current_states) {
      if (nfa.IsAccepted(state)) {
        std::cout << "Accepted." << std::endl;
        flag = true;
      }
      break;
    }
    if (!flag) {
      std::cout << "Not Accepted." << std::endl;
    }
  }
  current_states.clear();
  current_states.insert(nfa.GetStart());
  for (int i = 0; i < 10; i++) {
    current_states = nfa.Advance(current_states, i % 2 == 0 ? 'a' : 'b');
    bool flag = false;
    for (const auto &state : current_states) {
      if (nfa.IsAccepted(state)) {
        std::cout << "Accepted." << std::endl;
        flag = true;
      }
      break;
    }
    if (!flag) {
      std::cout << "Not Accepted." << std::endl;
    }
  }
  current_states.clear();
  current_states.insert(nfa.GetStart());
  for (int i = 0; i < 10; i++) {
    current_states = nfa.Advance(current_states, i % 2 == 0 ? 'b' : 'a');
    bool flag = false;
    for (const auto &state : current_states) {
      if (nfa.IsAccepted(state)) {
        std::cout << "Accepted." << std::endl;
        flag = true;
      }
      break;
    }
    if (!flag) {
      std::cout << "Not Accepted." << std::endl;
    }
  }
  return 0;
}