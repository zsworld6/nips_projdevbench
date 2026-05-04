#ifndef SRC_HPP
#define SRC_HPP
#include <iostream>
#include <utility>
struct Map;
enum class instruction{UP, DOWN, LEFT, RIGHT, NONE};
//the instruction of the snake

bool is_food(Map* map, int x, int y);
//return true if the cell at (x,y) is food

bool is_wall(Map* map, int x, int y);
//return true if the cell at (x,y) is wall

void eat_food(Map* map, int x, int y);
//remove the food at (x,y)

int get_height(Map* map);
//return the height of the map

int get_width(Map* map);
//return the width of the map


struct Snake{
  // store the necessary information of the snake
  // use any data structure you like
  // you can also add any necessary function
  //------------------------------------------
  // TODO
  
  void initialize(int x, int y, instruction ins){
    // (x,y) isthe position of the head of the snake, ins is the initial orientation of the snake
    //------------------------------------------
    // TODO
    
  }
  int get_length(){
    //return the length of the snake
    //------------------------------------------
    //TODO

  }
  bool move(Map* map, instruction ins){
    //the current map and the next instruction
    //return false if the snake is dead
    //return true if the snake is alive
    //------------------------------------------
    //TODO
    
  }
  std::pair<int, std::pair<int,int>*> get_snake(){
    //return the length of the snake and a pointer to the array of the position of the snake
    //you can store the head as the first element  
    //------------------------------------------
    //TODO
    
  }
};

const int MaxWidth = 20;
struct Map{
  // store the necessary information of the map
  bool wall[MaxWidth][MaxWidth];
  bool food[MaxWidth][MaxWidth];
  int width, height;
  int get_height(){
    //return the height of the map
    //TODO

  }
  int get_width(){
    //return the width of the map
    //TODO
    
  }
  bool is_food(int x, int y){
    //return true if the cell at (x,y) is food
    //TODO
    
  }
  void eat_food(int x, int y){
    //eat the food at (x,y)
    //TODO
    
  }
  bool is_wall(int x, int y){
    //return true if the cell at (x,y) is wall
    //TODO
    
  }
  // use any data structure you like
  // you can also add any necessary function
  //------------------------------------------
  //TODO
  


  void initialize(Snake *snake){
    char str[MaxWidth];
    int head_x = -1 , head_y = -1;
    instruction ins;
    //------------------------------------------
    //TODO
    
    
   
    //------------------------------------------
    snake->initialize(head_x, head_y, ins);
  }
  void print(Snake *snake){
    auto snake_body = snake->get_snake();
    //------------------------------------------
    //TODO
    
  }

};

struct Game{
  Map *map;
  Snake *snake;
  int score;
  int round;
  void initialize(){
    map = new Map();
    snake = new Snake();
    map->initialize(snake);
    score = 0;
    round = 0;
  }
  bool step()
  {
    char str[MaxWidth];
    std::cin >> str;
    instruction ins;
    switch(str[0]){
      case 'U':
        ins = instruction::UP;
        break;
      case 'D':
        ins = instruction::DOWN;
        break;
      case 'L':
        ins = instruction::LEFT;
        break;
      case 'R':
        ins = instruction::RIGHT;
        break;
      default:
        ins = instruction::NONE;
    }
    if(snake->move(map, ins)){
      score++;
    }else{
      return false;
    }
    return true;
  }
  void print(){
    std::cout<< "Round: " << round << std::endl;
    map->print(snake);
  }
  void play()
  {
    while(step()){
      round++;
      print();
    }
    score += snake->get_length() ;
    std::cout << "Game Over" << std::endl;
    std::cout << "Score: " << score << std::endl;
  }
};
#endif