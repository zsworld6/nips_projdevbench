/**
 * This is the student's part for Conway's Game of Life Simulator.
 * You need to finish all functions marked with "TODO" label.
 * When submitting, you should hand in THIS header file (i.e. game_of_life.h) to OJ to get correct mark.
 *
 * By the way, you SHOULD NOT try to read or write any extra information to the console.
 * Any attempt to hack the OJ or special judger WILL BE voided (and punished if it causes severe results).
 *
 * This is part of the 1st homework of Class A and 2nd homework of Class B. The workload isn't large.
 * We've also prepared a small visualizer for you. Enjoy coding ~
 */
#pragma once

#include <iostream>

/**
 * Feel free to define/modify variables here.
 */
inline int row = -1, col = -1;
inline bool game_map[50][50]{};
// TODO: Your variables here.

/**
 * This function is called at the beginning of every game.
 * Read the initial map of the game from stdin.
 * The format of the input is written in the problem description.
 *
 * TODO: Read the initial map from input and initialize your variables.
 */
inline void Initialize() {
  std::cin >> col >> row;
  // TODO(student): Implement me!
}

/**
 * This function is called once in every round of the game.
 * You need to simulate a round of game in this program.
 *
 * Note: You don't need to input or output anything. Just change the variables you defined so that they're in the new round.
 *
 * TODO: Simulate a new round of the game.
 */
inline void Tick() {
  // TODO(student): Implement me!
}

/**
 * This function may be called at any time during the game.
 * You need to print the map of the game in a certain format.
 * Output format is written in the problem description.
 *
 * Note: In this function, you just needs to print the map. DO NOT simulate a new round of game.
 *
 * TODO: Print the whole map.
 */
inline void PrintGame() {
  // TODO(student): Implement me!
}

/**
 * This function may be called at any time during the game.
 * You need to return the number of live cells.
 *
 * @returns the number of live cells in the map.
 *
 * Note: In this function, you SHOULD NOT simulate a new round of game or print anything to stdout.
 *
 * TODO: Returns the number of live cells.
 */
inline int GetLiveCell() {
  return 0;
  // TODO(student): Implement me!
}