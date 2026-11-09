#如何运行：可以一键运行launch文件ros2 launch py02 test_projection.launch.py
#	或在各终端逐条运行1、ros2 run py02 static_tf_broadcaster
#	2、ros2 bag play sample_bag --clock -l
#	3、ros2 run py02 sync_node --ros-args -p use_sim_time:=true -p slop:=0.019
#	4、rqt_image_view（务必要在左上角选取/projection/debug_image）

#TF树说明：base_link是laser_link和camera_link的父坐标系，坐标分别为  
  xyz:
  - 0.15
  - 0.0
  - 0.2
  rpy:
  - 0.0
  - 0.0
  - 0.0
和
  xyz:
  - 0.1
  - 0.0
  - 0.3
  rpy:
  - 0.0
  - 0.0
  - 0.0
#slop选择说明：
#一开始选用50作为接受队列长度，从0.005扫到0.15，但发现不太正常，slop越过0.02后配上的帧数会下降和波动，于是我换了一个200帧的数据包，把队列长度改为60，从0.005测试到0.04，发现到了0.019后就配对完200帧了，越往后精度反而越低，于是选择0.019作为默认slop

#use_sim_time对比结论：无差异
#解释：虽然系统时间和 Bag 时间相差巨大，但我通过精准传入 header.stamp 进行 TF 查询，并利用静态 TF 0 时间戳永久有效的特性，使得我的融合算法即便在 use_sim_time=False 的恶劣情况下依然能稳定运行。但为了规范，仍推荐设为 true
