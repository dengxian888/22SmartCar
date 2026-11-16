版本 					输入 	     /perception/result 	/control/cmd 	 P95 延迟
基线（camera_pub.py + image_proc.py） 	≈ 15.6 Hz 	≈ 2.3 Hz 	≈ 2.3 Hz 	≈ 2443 ms
你的版本 				30.0Hz 		30.0Hz		20.0Hz	 	  19Hz


#牺牲了数据完整性（丢帧换低延迟）：将订阅端的 QoS depth 从大数值改为了 2，在系统 CPU 偶尔出现波动或处理不过来时，系统会主动丢弃积压在队列里的旧帧，只抓取最新的一帧进行处理
#牺牲了“瞬时内存与算力”：在图像处理中，把原生的 Python 整数运算替换成了 NumPy 的 int16 和 float32 运算，单帧图像在计算时，内存占用量会成倍增加，改成多线程（MultiThreadedExecutor）后，操作系统调度多核 CPU 也会带来额外的上下文切换开销

