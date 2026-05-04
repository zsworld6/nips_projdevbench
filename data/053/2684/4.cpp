#include "src.hpp"
#include <bits/stdc++.h>
#include <iostream>
#include <unordered_set>
int main() {
  // abb+b?
  auto nfa_a = Grammar::MakeSimple('a');
  auto nfa_b = Grammar::MakeSimple('b');
  auto nfa = Grammar::Concatenate(nfa_a, nfa_b);
  nfa = Grammar::Concatenate(nfa, Grammar::MakePlus('b'));
  nfa = Grammar::Concatenate(nfa, Grammar::MakeQuestion('b'));
  std::string test[4];
  test[0] = "abbb";
  test[1] = "aabbb";
  test[2] = "aba";
  test[3] = "abbbbbbbbbbbbb";
  for (auto str : test) {
    std::unordered_set<int> current_states;
    current_states.insert(nfa.GetStart());
    for (auto ch : str) {
      current_states = nfa.Advance(current_states, ch);
    }
    bool flag = false;
    for (const auto &state : current_states) {
      if (nfa.IsAccepted(state)) {
        std::cout << str << " Accepted." << std::endl;
        flag = true;
        break;
      }
    }
    if (!flag) {
      std::cout << str << " Not Accepted." << std::endl;
    }
  }
  nfa = Grammar::Concatenate(nfa_a, nfa_b);
  nfa = Grammar::Concatenate(nfa, Grammar::MakePlus('a'));
  nfa = Grammar::Concatenate(nfa, Grammar::MakeQuestion('b'));
  // aba+b?
  for (auto str : test) {
    std::unordered_set<int> current_states;
    current_states.insert(nfa.GetStart());
    for (auto ch : str) {
      current_states = nfa.Advance(current_states, ch);
    }
    bool flag = false;
    for (const auto &state : current_states) {
      if (nfa.IsAccepted(state)) {
        std::cout << str << " Accepted." << std::endl;
        flag = true;
        break;
      }
    }
    if (!flag) {
      std::cout << str << " Not Accepted." << std::endl;
    }
  }
  return 0;
}