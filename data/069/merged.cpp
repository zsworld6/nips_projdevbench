#include <cstddef>
#include <cstdint>
#include <algorithm>

namespace sjtu {

const size_t MEMORY_SIZE = 1024 * 1024; // 1 MB

// 内存块结构体
struct MemoryBlock{
    int address;
    int size;
    bool is_free;

    // 链表指针
    MemoryBlock* next = nullptr;
};

// 全局变量
// TODO 你可以自由添加其他变量
MemoryBlock* head = nullptr; // 内存块链表头指针

// ------- 辅助函数 ------- //

/**
 * @brief 将一个大的内存块拆分为两块。
 * @param block 要拆分的内存块
 * @param size 拆分后原内存块的大小
 * @return 拆分后新块的指针（如果拆分失败,返回nullptr）
 */
inline MemoryBlock* splitBlock(MemoryBlock* block, size_t size) {
    if (block->size < size + sizeof(MemoryBlock)) {
        return nullptr; // 无法拆分
    }
    // 创建新的内存块
    MemoryBlock* new_block = new MemoryBlock;
    new_block->address = block->address + sizeof(MemoryBlock) + size;
    new_block->size = block->size - size - sizeof(MemoryBlock);
    new_block->is_free = true;
    new_block->next = block->next;
    // 更新原内存块
    block->size = size;
    block->next = new_block;

    return new_block;
}

/**
 * @brief 合并相邻的内存块。
 * @param block 要合并的内存块
*/
inline void mergeBlock(MemoryBlock* block){
    MemoryBlock* next = block->next;
    if (next == nullptr) {
        return;
    }
    block->size += sizeof(MemoryBlock) + next->size;
    block->next = next->next;
    delete next;
}

// ------ 以下是你要实现的内存分配和释放函数 ------ //

/**
 * @brief 分配指定大小的内存块。
 * @param size 要分配的内存大小（以字节为单位）
 * @return 指向分配内存块的指针（如果内存不足,返回nullptr）
 */
inline MemoryBlock* allocate(int size){
    // TODO 请自行实现内存分配的逻辑
    return nullptr;
}

/**
 * @brief 释放之前分配的内存块。
 * @param ptr 指向要释放的内存块的指针
 */
inline void deallocate(MemoryBlock* ptr){
    // TODO 请自行实现内存分配的逻辑
}
/**
 * @brief 重置内存管理器，初始化内存块链表。如果你在实现中使用了额外的全局变量，请在此函数中进行初始化。
 */
inline void resetMemory(){
    // 释放之前的链表
    MemoryBlock* temp = head;
    while (temp) {
        MemoryBlock* next = temp->next;
        delete temp;
        temp = next;
    }
    
    // 初始化新的内存块链表
    head = new MemoryBlock;
    head->address = 0;
    head->size = MEMORY_SIZE - sizeof(MemoryBlock);
    head->is_free = true;
}

} // namespace sjtu


#include <iostream>

using namespace sjtu;

bool testNormalAlloc(){
    resetMemory();
    MemoryBlock* block1 = allocate(256);
    if (!block1 || block1->size < 256 || !block1->is_free == false) return false;
    return true;
}

bool testSmallAlloc(){
    resetMemory();
    MemoryBlock* block1 = allocate(1); // 请求过小内存
    if (!block1 || block1->size < 1 || !block1->is_free == false) return false;
    return true;
}

bool testBigAlloc(){
    resetMemory();
    const int MAX_SIZE = MEMORY_SIZE - sizeof(MemoryBlock);
    MemoryBlock* block1 = allocate(MAX_SIZE); // 请求过大内存
    if (!block1 || block1->size < MAX_SIZE || !block1->is_free == false) return false;
    return true;
}

bool testOverAlloc(){
    resetMemory();
    const int MAX_SIZE = MEMORY_SIZE - sizeof(MemoryBlock);
    MemoryBlock* block1 = allocate(MAX_SIZE + 1); // 请求过大内存
    if (block1 != nullptr) return false;
    return true;
}

bool testTwoAlloc(){
    resetMemory();
    MemoryBlock* block1 = allocate(256);
    if(!block1 || block1->size < 256 || !block1->is_free == false) return false;

    MemoryBlock* block2 = allocate(128);
    if(!block2 || block2->size < 128 || !block2->is_free == false) return false;

    if(block1->next != block2) return false;

    return true;
}

bool testMultiAlloc(){
    resetMemory();
    const int ALLOC_SIZES[] = {64, 128, 256, 512, 1024, 2048, 4096};

    MemoryBlock* prev_block = nullptr;
    for(auto size: ALLOC_SIZES){
        MemoryBlock* block = allocate(size);
        if(!block || block->size < size || !block->is_free == false) return false;
        if(prev_block && prev_block->next != block) return false;
        prev_block = block;
    }

    return true;
}

bool testMultiAllocUntilFull(){
    resetMemory();
    const int ALLOC_SIZE = 1024; // 每次分配1KB
    const int MAX_BLOCKS = MEMORY_SIZE / (ALLOC_SIZE + sizeof(MemoryBlock));

    MemoryBlock* prev_block = nullptr;
    for(int i = 0; i < MAX_BLOCKS; ++i){
        MemoryBlock* block = allocate(ALLOC_SIZE);
        if(!block || block->size < ALLOC_SIZE || !block->is_free == false) return false;
        if(prev_block && prev_block->next != block) return false;
        prev_block = block;
    }

    // 再次分配应该失败
    MemoryBlock* block = allocate(ALLOC_SIZE);
    if(block != nullptr) return false;

    return true;
}

bool testAllocAndDealloc(){
    resetMemory();
    MemoryBlock* block1 = allocate(256);
    if(!block1 || block1->size < 256 || !block1->is_free == false) return false;
    
    deallocate(block1);
    if(block1->is_free == false) return false;

    MemoryBlock* block2 = allocate(128);
    if(!block2 || block2->size < 128 || !block2->is_free == false) return false;

    if(block1 != block2) return false; // 应该复用之前释放的内存块
    return true;
}

bool testMultiAllocAndDealloc(){
    resetMemory();
    MemoryBlock* blocks[5];
    for(int i = 0; i < 5; ++i){
        blocks[i] = allocate(256);
        if(!blocks[i] || blocks[i]->size < 256 || !blocks[i]->is_free == false) return false;
    }
    // 释放中间的块
    deallocate(blocks[2]);
    if(blocks[2]->is_free == false) return false;
    // 分配一个更小的块，应该复用之前释放的块
    MemoryBlock* block_small = allocate(128);
    if(!block_small || block_small->size < 128 || !block_small->is_free == false) return false;
    if(block_small != blocks[2]) return false;
    return true;
}

bool testAllAllocAndDealloc(){
    resetMemory();
    const int ALLOC_SIZE = 1024; // 每次分配512B
    const int MAX_BLOCKS = MEMORY_SIZE / (ALLOC_SIZE + sizeof(MemoryBlock));

    MemoryBlock* blocks[MAX_BLOCKS];
    for(int i = 0; i < MAX_BLOCKS; ++i){
        blocks[i] = allocate(ALLOC_SIZE);
        if(!blocks[i] || blocks[i]->size < ALLOC_SIZE || !blocks[i]->is_free == false) return false;
    }

    // 释放所有块
    for(int i = MAX_BLOCKS-1; i >= 0; --i){
        deallocate(blocks[i]);
        if(blocks[i]->is_free == false) return false;
    }

    //分配大块
    MemoryBlock* big_block = allocate(MEMORY_SIZE - sizeof(MemoryBlock) - 1);;
    if(!big_block || big_block->size < MEMORY_SIZE - sizeof(MemoryBlock) - 1 || !big_block->is_free == false) return false;
    return true;
}

int main(){
    std::cout << "Test Normal Alloc: " << (testNormalAlloc() ? "Passed" : "Failed") << std::endl;
    std::cout << "Test Small Alloc: " << (testSmallAlloc() ? "Passed" : "Failed") << std::endl;
    std::cout << "Test Big Alloc: " << (testBigAlloc() ? "Passed" : "Failed") << std::endl;
    std::cout << "Test Over Alloc: " << (testOverAlloc() ? "Passed" : "Failed") << std::endl;
    std::cout << "Test Two Alloc: " << (testTwoAlloc() ? "Passed" : "Failed") << std::endl;
    std::cout << "Test Multi Alloc: " << (testMultiAlloc() ? "Passed" : "Failed") << std::endl;
    std::cout << "Test Multi Alloc Until Full: " << (testMultiAllocUntilFull() ? "Passed" : "Failed") << std::endl;
    std::cout << "Test Alloc And Dealloc: " << (testAllocAndDealloc() ? "Passed" : "Failed") << std::endl;
    std::cout << "Test Multi Alloc And Dealloc: " << (testMultiAllocAndDealloc() ? "Passed" : "Failed") << std::endl;
    std::cout << "Test All Alloc And Dealloc: " << (testAllAllocAndDealloc() ? "Passed" : "Failed") << std::endl;
    return 0;
}