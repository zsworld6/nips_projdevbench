// Copyright (c) 2024 ACM Class, SJTU

namespace sjtu {

class BuddyAllocator {
public:
  /**
   * @brief Construct a new Buddy Allocator object with the given RAM size and
   * minimum block size.
   *
   * @param ram_size Size of the RAM. The address space is 0 ~ ram_size - 1.
   * @param min_block_size Minimum size of a block. The block size is 2^k where
   * k >= min_block_size.
   */
  BuddyAllocator(int ram_size, int min_block_size) {
    // TODO(student): Implement this function.
  }

  /**
   * @brief Allocate a block with the given size at the minimum available
   * address.
   *
   * @param size The size of the block.
   * @return int The address of the block. Return -1 if the block cannot be
   * allocated.
   */
  int malloc(int size) {
    // TODO(student): Implement this function.
    return -1;
  }

  /**
   * @brief Allocate a block with the given size at the given address.
   *
   * @param addr The address of the block.
   * @param size The size of the block.
   * @return int The address of the block. Return -1 if the block cannot be
   * allocated.
   */
  int malloc_at(int addr, int size) {
    // TODO(student): Implement this function.
    return -1;
  }

  /**
   * @brief Deallocate a block with the given size at the given address.
   *
   * @param addr The address of the block. It is ensured that the block is
   * allocated before.
   * @param size The size of the block.
   */
  void free_at(int addr, int size) {
    // TODO(student): Implement this function.
  }

private:
  // Add whatever you need here.
};

} // namespace sjtu