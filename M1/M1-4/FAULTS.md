#问题一：
#现象：终端运行python3 camera_pub.py发现平均Hz低于目标Hz
#定位：capture函数里for双循环造图（与AI对话得知）
#根因：图片大小为640*480，逐像素造图要执行307200次，对解释器的负担很大，需要约50~80ms
#修复：将for双循环替换为numpy矩阵，利用了numpy矩阵的广播机制
#验证：运行python3 camera_pub.py，发现平均接近30Hz

#问题二：
#现象：终端运行ros2 topic delay /perception/result发现平均延迟远高达1280ms
#定位：image_proc.py文件里的make_sub_qos函数的depth设置过大，为30（根据手册排除问题得知）
#根因：接收信息队列过长，导致旧消息不能及时被抛弃处理，新信息等待过久，信息堆积，导致延迟累积
#修复：将depth改为2
#验证：运行ros2 topic delay /perception/result，发现平均延迟降低到340ms

#问题三：
#现象：终端运行ros2 topic hz /perception/result发现平均Hz还是远低于目标Hz，仅3.8Hz,而运行ros2 topic hz /control/cmd发现平均Hz仅有3.2Hz
#定位：on_image函数处理原图有问题（由问题一可见一斑）
#根因：提亮和对比度增强用了双重for循环，而且还做了放大再缩小
#修复：都改为用numpy矩阵运算，且删除了放大再缩小
#验证：运行ros2 topic hz /perception/result，平均Hz能稳定在30Hz,运行ros2 topic hz /control/cmd，平均Hz能稳定在20Hz,而延迟也降到22ms左右

#问题四：
#现象：单线程执行器导致控制指令被图像回调阻塞
#定位：main函数里的SingleThreadedExecutor（根据手册排除问题得知）
#根因：单线程，处理图像时根本没空去发控制指令，需要改成多线程执行器
#修复：将SingleThreadedExecutor换为MultiThreadedExecutor，让图像回调和控制回调用ReentrantCallbackGroup分到不同的线程
#验证：延迟进一步降低至19ms
