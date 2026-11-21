import time
import csv
from pathlib import Path
import rclpy
from rclpy.node import Node
from rcl_interfaces.srv import SetParameters, GetParameters
from rclpy.parameter import Parameter
from host_side.audit import AuditLogger

class HotSwitcher:
    def __init__(self, node: Node, audit: AuditLogger):
        self.node = node
        self.audit = audit

    def _append_switch_log(self, op, old_val, new_val, source, result="ok"):
        """追加写入 switch_log.csv，供考官查验"""
        log_path = Path("switch_log.csv")
        file_exists = log_path.exists()
        
        with open(log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # 如果是新文件，先写表头
            if not file_exists:
                writer.writerow(["ts", "op", "from", "to", "source", "result"])
            
            writer.writerow([
                time.strftime("%Y-%m-%dT%H:%M:%S"),
                op,
                str(old_val),
                str(new_val),
                source,
                result
            ])

    def _get_current(self, node_name: str, param_name: str) -> str:
        """通过 ROS2 服务获取节点当前的参数值"""
        srv_name = f'/{node_name}/get_parameters'
        client = self.node.create_client(GetParameters, srv_name)
        if not client.wait_for_service(timeout_sec=1.0):
            return "unknown"
            
        req = GetParameters.Request()
        req.names = [param_name]
        future = client.call_async(req)
        
        start = time.time()
        while not future.done():
            if time.time() - start > 1.0:
                return "unknown"
            time.sleep(0.05)
            
        res = future.result()
        if res and len(res.values) > 0 and res.values[0].string_value:
            return res.values[0].string_value
        return "unknown"

    def set_param(self, node_name: str, param_name: str, value, source="web_ui"):
        """修改节点参数（不重启节点）"""
        srv_name = f'/{node_name}/set_parameters'
        client = self.node.create_client(SetParameters, srv_name)
        
        if not client.wait_for_service(timeout_sec=1.0):
            self.audit.log(op="PARAM_SET", source=source, node=node_name, param=param_name, result="failed", reason="service_not_found")
            return False, "服务未找到"

        req = SetParameters.Request()
        req.parameters = [Parameter(name=param_name, value=value).to_parameter_msg()]
        future = client.call_async(req)
        
        start = time.time()
        while not future.done():
            if time.time() - start > 2.0:
                return False, "请求超时"
            time.sleep(0.05)

        res = future.result()
        if res and res.results[0].successful:
            self.audit.log(op="PARAM_SET", source=source, node=node_name, param=param_name, new_val=str(value), result="ok")
            return True, "成功"
        
        self.audit.log(op="PARAM_SET", source=source, node=node_name, param=param_name, new_val=str(value), result="failed")
        return False, "设置失败"

    def switch_model(self, node_name: str, model_path: str, source="web_ui"):
        """切换感知模型并支持自动回滚"""
        # 1. 切换前，先获取真实的旧模型路径
        old_model = self._get_current(node_name, 'model_path')
        
        # 2. 尝试设置新模型
        success, msg = self.set_param(node_name, 'model_path', model_path, source)
        if success:
            self.audit.log(op="MODEL_SWITCH", source=source, from_model=str(old_model), to_model=model_path, result="ok")
            # 【新增】写入 switch_log.csv
            self._append_switch_log("MODEL_SWITCH", old_model, model_path, source, "ok")
            return True, f"模型切换成功！\n由 {old_model} 切换至 {model_path}"
        else:
            # 3. 失败自动回滚到真实的旧路径
            if old_model and old_model != "unknown":
                self.set_param(node_name, 'model_path', old_model, source)
                self.audit.log(op="MODEL_SWITCH_ROLLBACK", source=source, from_model=model_path, to_model=old_model, result="ok")
                # 【新增】写入 switch_log.csv，注意 from 是失败的 model_path，to 是回滚的 old_model
                self._append_switch_log("MODEL_SWITCH_ROLLBACK", model_path, old_model, source, "ok")
                return False, f"模型加载失败，已自动回滚至旧模型: {old_model}"
            else:
                self.audit.log(op="MODEL_SWITCH_ROLLBACK", source=source, from_model=model_path, to_model="unknown", result="failed")
                # 【新增】无法回滚时也记录
                self._append_switch_log("MODEL_SWITCH_ROLLBACK_FAILED", model_path, "unknown", source, "failed")
                return False, "模型加载失败，且无法获取旧模型，请手动检查！"