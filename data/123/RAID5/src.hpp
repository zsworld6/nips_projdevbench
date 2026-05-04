#include "fstream.h"
#include <vector>

// 磁盘事件类型：正常、故障、更换
enum class EventType {
  NORMAL,  // 正常：所有磁盘工作正常
  FAILED,  // 故障：指定磁盘发生故障（文件被删除）
  REPLACED // 更换：指定磁盘被更换（文件被清空）
};

class RAID5Controller {
private:
  std::vector<sjtu::fstream *> drives_; // 磁盘文件对应的 fstream 对象
  int blocks_per_drive_;               // 每个磁盘的块数
  int block_size_;                     // 每个块的大小
  int num_disks_;                      // 磁盘数
public:
  RAID5Controller(std::vector<sjtu::fstream *> drives, int blocks_per_drive,
                  int block_size = 4096) {
    // 输入“磁盘”（文件）对应的 fstream* 对象。
    // drives.size() 即为磁盘个数
    // 文件已经存在且大小为 block_size * blocks_per_drive
    // 文件初始数据为全 0
  }

  /**
   * @brief 启动 RAID5 系统
   * @param event_type_ 磁盘事件类型
   * @param drive_id 发生事件的磁盘编号（如果是 NORMAL 则忽略）
   *
   * 如果是 FAILED，对应的磁盘文件会被删除。此时不可再对该文件进行读写。
   * 如果是 REPLACED，对应的磁盘文件会被清空（但文件依然存在）
   * 如果是 NORMAL，所有磁盘正常工作
   * 注：磁盘被替换之前不一定损坏。
   */
  void Start(EventType event_type_, int drive_id) {
    // TODO
  }

  void Shutdown() {
    // 关闭所有打开的文件，以防未定义行为发生。
    // TODO
  }

  void ReadBlock(int block_id, char *result) {
    // 读取第 block_id 个块的内容，写入 result 中
    // TODO
  }

  void WriteBlock(int block_id, const char *data) {
    // 将 data 中的内容写入第 block_id 个块中
    // TODO
  }

  int Capacity() {
    // 返回磁盘阵列能写入的块的数量（你无需改动此函数）
    return (num_disks_ - 1) * blocks_per_drive_;
  }
};