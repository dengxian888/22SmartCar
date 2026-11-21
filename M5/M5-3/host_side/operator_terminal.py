import argparse
import threading
import rclpy
from rclpy.executors import MultiThreadedExecutor
from flask import Flask, render_template, request, jsonify
from std_msgs.msg import String

from host_side.audit import AuditLogger
from host_side.safety import SafetyLayer
from host_side.hot_switch import HotSwitcher
from host_side.referee_bridge import RefereeBridge

app = Flask(__name__)

# 全局句柄
safety = None
switcher = None
referee_bridge = None

# ==========================================
# 核心：统一命令总线 (防两套逻辑)
# ==========================================
def execute_command(cmd_type: str, source: str):
    """
    所有操作（无论是 Web 点击、物理按键还是语音唤醒）
    都必须汇聚到这里执行。
    """
    if cmd_type == "estop":
        if safety:
            safety.trigger_emergency_stop(source=source, reason="multi_modal_trigger")
            return True, "急停已触发"
    
    elif cmd_type in ["START", "PAUSE", "RESUME", "STOP", "PENALTY"]:
        if referee_bridge:
            msg = String()
            msg.data = cmd_type
            # 注入来源，让裁判节点记录是谁触发的
            referee_bridge.referee_callback(msg, trigger_source=source)
            return True, f"裁判指令 {cmd_type} 已执行"
            
    return False, "未知指令类型"

# ==========================================
# Web API 路由
# ==========================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config')
def api_config():
    import yaml
    try:
        with open('config/terminal.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/estop', methods=['POST'])
def api_estop():
    success, msg = execute_command("estop", source="web_ui")
    return jsonify({"status": "ok" if success else "error", "msg": msg})

@app.route('/api/referee', methods=['POST'])
def api_referee():
    cmd = request.json.get('cmd')
    success, msg = execute_command(cmd, source="web_ui")
    return jsonify({"status": "ok" if success else "error", "msg": msg})

@app.route('/api/switch_model', methods=['POST'])
def api_switch_model():
    data = request.json
    model_path = data.get('model_path')
    if switcher:
        success, msg = switcher.switch_model("perception_node", model_path, source="web_ui")
        return jsonify({"success": success, "msg": msg})
    return jsonify({"status": "error", "msg": "系统未就绪"}), 500

@app.route('/api/status')
def api_status():
    state = referee_bridge.state if referee_bridge else "OFFLINE"
    return jsonify({"ref_state": state})

# ==========================================
# 新增：外部硬件/语音触发接口
# ==========================================
@app.route('/api/physical_trigger', methods=['POST'])
def api_physical_trigger():
    """
    供物理按键脚本、串口读取程序或离线语音识别模块调用
    请求体: {"trigger": "estop" | "START" | "PAUSE" | "RESUME", "source": "voice_offline" | "physical_button"}
    """
    data = request.json or {}
    trigger = data.get('trigger')
    source = data.get('source', 'physical_device')
    
    if not trigger:
        return jsonify({"status": "error", "msg": "缺少 trigger 参数"}), 400
        
    success, msg = execute_command(trigger, source=source)
    return jsonify({"status": "ok" if success else "error", "msg": msg})

# ==========================================
# 主函数
# ==========================================
def main():
    global safety, switcher, referee_bridge
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8081)
    args = parser.parse_args()

    rclpy.init()
    audit = AuditLogger()
    
    host_node = rclpy.create_node('host_terminal_node')
    safety = SafetyLayer(audit)
    switcher = HotSwitcher(host_node, audit)
    referee_bridge = RefereeBridge(audit)
    
    executor = MultiThreadedExecutor()
    executor.add_node(safety)
    executor.add_node(referee_bridge)
    executor.add_node(host_node)
    
    def spin_executor():
        try:
            executor.spin()
        except Exception as e:
            print(f"Executor spin exited: {e}")

    threading.Thread(target=spin_executor, daemon=True).start()

    print(f"🚀 Web 终端已启动，请在浏览器访问: http://127.0.0.1:{args.port}")
    app.run(host='0.0.0.0', port=args.port, debug=False)

if __name__ == '__main__':
    main()