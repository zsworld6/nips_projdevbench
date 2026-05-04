#include "src.hpp"
#include <bits/stdc++.h>
#include <iostream>
#include <unordered_set>
int main() {
  auto nfa1 = Grammar::MakeSimple('a');
  auto nfa2 = Grammar::MakeSimple('b');
  auto nfa3 = Grammar::MakeSimple('a');
  auto nfa = Grammar::Concatenate(Grammar::Concatenate(nfa1, nfa2), nfa3);
  std::unordered_set<int> current_states;
  current_states.insert(nfa.GetStart());
  for (int i = 0; i < 10; i++) {
    current_states = nfa.Advance(current_states, 'a');
    bool flag = false;
    for (const auto &state : current_states) {
      if (nfa.IsAccepted(state)) {
        std::cout << "Accepted." << std::endl;
        flag = true;
        break;
      }
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
        break;
      }
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