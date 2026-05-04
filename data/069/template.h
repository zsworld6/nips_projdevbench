#pragma once

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
