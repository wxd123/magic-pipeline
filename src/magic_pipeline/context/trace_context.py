# trace_context.py
# 通用审计追踪上下文 - 零业务依赖

import uuid
import hashlib
import hmac
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


# ==================== 枚举定义 ====================

class LayerType(str, Enum):
    """层级类型 - 四层追踪架构"""
    AGENT = "agent"
    PIPELINE = "pipeline"
    STEP = "step"
    COMMAND = "command"


class AuditStatus(str, Enum):
    """审计状态"""
    START = "start"
    SUCCESS = "success"
    ERROR = "error"


# ==================== 审计事件定义 ====================

@dataclass
class AuditEvent:
    """
    审计事件 - 最小审计单位
    
    双字段设计：
    - request_id: 标准请求ID（固定为Agent层ID，用于查询完整链路）
    - extend_request_id: 扩展请求ID（包含完整调用链，用于查询子链路）
    """

    trace_id: str                # 全局追踪ID
    # === 双字段标识（核心）===
    request_id: str              # 标准请求ID（Agent层ID，整个调用链不变）
    extend_request_id: str       # 扩展请求ID（包含完整调用链）
    
    # 操作者标识
    operator_id: str       # 操作者ID（用户/服务/系统）
    operator_name: str     # 操作者名称（可选）
    
    
    layer: str                   # agent/pipeline/step/command
    
    
    # === 状态信息 ===
    status: AuditStatus
    timestamp: str
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    message: Optional[str] = None
    
    # === 输入输出快照 ===
    input_snapshot: Optional[Dict[str, Any]] = None
    output_snapshot: Optional[Dict[str, Any]] = None
    
    # === 审计链完整性 ===
    previous_hash: Optional[str] = None
    hash: Optional[str] = None
    
    # === 扩展元数据 ===
    tags: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "request_id": self.request_id,
            "extend_request_id": self.extend_request_id,
            "trace_id": self.trace_id,
            "operator_id": self.operator_id,
            "operator_name": self.operator_name,
            "layer": self.layer,            
            "status": self.status.value,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "message": self.message,
            "input_snapshot": self.input_snapshot,
            "output_snapshot": self.output_snapshot,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "tags": self.tags
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)


# ==================== 审计上下文 ====================

class TraceContext:
    """
    通用审计追踪上下文
    
    设计原则：
    1. 只负责审计业务管理，不负责全局集成
    2. 双字段设计：request_id（标准）+ extend_request_id（扩展）
    3. 支持四层追踪：Agent → Pipeline → Step → Command
    4. 审计链哈希保证完整性
    5. 零业务依赖，纯通用审计功能
    
    使用方式：
        
        
        # Agent层
        trace.start_agent()
        try:
            # Pipeline层
            trace.start_pipeline("comment_pipeline")
            
            # Step层
            trace.start_step("java_generate")
            
            # Command层
            trace.start_command("generate")
            trace.set_output_snapshot({"result": "success"})
            trace.success_command()
            
            trace.success_step()
            trace.success_pipeline()
            trace.success_agent()
        except Exception as e:
            trace.error_agent(str(e))
        
        # 获取审计结果
        events = trace.get_audit_chain()
        report = trace.export_audit_chain()
    """
    
    def __init__(
        self, 
        trace_id: Optional[str] = None,
        secret_key: Optional[str] = None
    ):
        """
        初始化审计上下文
        
        Args:
            session_id: 会话ID（由全局上下文提供）
            agent_component: Agent组件名称
            trace_id: 追踪ID，不提供则自动生成
            secret_key: 签名密钥，用于防篡改
        """
        # === 基础标识 ===
        
        self.trace_id = trace_id or self._generate_trace_id()
        self.secret_key = secret_key or "default_secret"
        
        
        # === 双字段（核心）===
        # request_id: 标准请求ID，固定为Agent层ID
        self._base_request_id: Optional[str] = None
        # extend_request_id: 扩展请求ID，随层级增长
        self._current_extend_request_id: Optional[str] = None
        
        # === 层级请求ID缓存 ===
        self._agent_request_id: Optional[str] = None
        self._pipeline_request_id: Optional[str] = None
        self._step_request_id: Optional[str] = None
        self._command_request_id: Optional[str] = None
        
        # === 审计链 ===
        self._events: List[AuditEvent] = []
        self._last_hash = "0" * 64
        
        # === 当前状态 ===
        self._current_layer: Optional[LayerType] = None
        self._current_component: Optional[str] = None
        self._current_event: Optional[AuditEvent] = None
        self._layer_start_times: Dict[LayerType, datetime] = {}
        
        # === 层级关系 ===
        self._parent_components: Dict[LayerType, Optional[str]] = {
            LayerType.AGENT: None,
            LayerType.PIPELINE: None,
            LayerType.STEP: None,
            LayerType.COMMAND: None
        }
    
    # ==================== 公共API ====================
    
    # --- Agent层 ---
    
    def start_agent(self, message: str = "") -> AuditEvent:
        """开始Agent层"""
        self._current_layer = LayerType.AGENT
        self._current_component = self.agent_component
        
        # 构建双字段ID
        self._agent_request_id = self._build_request_id(LayerType.AGENT)
        self._base_request_id = self._agent_request_id
        self._current_extend_request_id = self._agent_request_id
        
        return self._start(LayerType.AGENT, self.agent_component, message)
    
    def success_agent(self, message: str = "") -> AuditEvent:
        """Agent层成功"""
        return self._success(message)
    
    def error_agent(self, error_message: str) -> AuditEvent:
        """Agent层错误"""
        return self._error(error_message)
    
    # --- Pipeline层 ---
    
    def start_pipeline(self, component: str, message: str = "") -> AuditEvent:
        """开始Pipeline层"""
        self._current_layer = LayerType.PIPELINE
        self._current_component = component
        
        self._pipeline_request_id = self._build_request_id(LayerType.PIPELINE)
        self._current_extend_request_id = self._pipeline_request_id
        self._parent_components[LayerType.PIPELINE] = self.agent_component
        
        return self._start(LayerType.PIPELINE, component, message)
    
    def success_pipeline(self, message: str = "") -> AuditEvent:
        """Pipeline层成功"""
        return self._success(message)
    
    def error_pipeline(self, error_message: str) -> AuditEvent:
        """Pipeline层错误"""
        return self._error(error_message)
    
    # --- Step层 ---
    
    def start_step(self, component: str, message: str = "") -> AuditEvent:
        """开始Step层"""
        self._current_layer = LayerType.STEP
        self._current_component = component
        
        self._step_request_id = self._build_request_id(LayerType.STEP)
        self._current_extend_request_id = self._step_request_id
        self._parent_components[LayerType.STEP] = self._current_component
        
        return self._start(LayerType.STEP, component, message)
    
    def success_step(self, message: str = "") -> AuditEvent:
        """Step层成功"""
        return self._success(message)
    
    def error_step(self, error_message: str) -> AuditEvent:
        """Step层错误"""
        return self._error(error_message)
    
    # --- Command层 ---
    
    def start_command(self, component: str, message: str = "") -> AuditEvent:
        """开始Command层"""
        self._current_layer = LayerType.COMMAND
        self._current_component = component
        
        self._command_request_id = self._build_request_id(LayerType.COMMAND)
        self._current_extend_request_id = self._command_request_id
        self._parent_components[LayerType.COMMAND] = self._current_component
        
        return self._start(LayerType.COMMAND, component, message)
    
    def success_command(self, message: str = "") -> AuditEvent:
        """Command层成功"""
        return self._success(message)
    
    def error_command(self, error_message: str) -> AuditEvent:
        """Command层错误"""
        return self._error(error_message)
    
    # --- 辅助方法 ---
    
    def set_input_snapshot(self, input_data: Any) -> None:
        """设置输入快照"""
        if self._current_event:
            self._current_event.input_snapshot = self._serialize(input_data)
    
    def set_output_snapshot(self, output_data: Any) -> None:
        """设置输出快照"""
        if self._current_event:
            self._current_event.output_snapshot = self._serialize(output_data)
    
    def set_tag(self, key: str, value: Any) -> None:
        """设置标签"""
        if self._current_event:
            self._current_event.tags[key] = value
    
    # --- 查询方法 ---
    
    def get_current_request_id(self) -> str:
        """获取当前层级的扩展请求ID"""
        return self._current_extend_request_id or ""
    
    def get_base_request_id(self) -> str:
        """获取标准请求ID（Agent层ID）"""
        return self._base_request_id or ""
    
    def get_trace_id(self) -> str:
        """获取追踪ID"""
        return self.trace_id
    
    def get_session_id(self) -> str:
        """获取会话ID"""
        return self.session_id
    
    def get_audit_chain(self) -> List[AuditEvent]:
        """获取完整审计链"""
        return self._events.copy()
    
    def verify_chain_integrity(self) -> bool:
        """验证审计链完整性"""
        prev_hash = "0" * 64
        for event in self._events:
            if event.previous_hash != prev_hash:
                return False
            expected_hash = self._calculate_hash(event)
            if event.hash != expected_hash:
                return False
            prev_hash = event.hash
        return True
    
    def export_audit_chain(self, format: str = "json") -> str:
        """导出审计链"""
        if format == "json":
            return json.dumps(
                [e.to_dict() for e in self._events],
                ensure_ascii=False,
                default=str,
                indent=2
            )
        return str(self._events)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取审计统计信息"""
        if not self._events:
            return {"total_events": 0}
        
        start_events = [e for e in self._events if e.status == AuditStatus.START]
        success_events = [e for e in self._events if e.status == AuditStatus.SUCCESS]
        error_events = [e for e in self._events if e.status == AuditStatus.ERROR]
        
        return {
            "total_events": len(self._events),
            "start_count": len(start_events),
            "success_count": len(success_events),
            "error_count": len(error_events),
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "base_request_id": self._base_request_id,
            "integrity_valid": self.verify_chain_integrity()
        }
    
    def clear(self) -> None:
        """清空审计上下文（保留基础标识）"""
        self._events = []
        self._last_hash = "0" * 64
        self._current_event = None
        self._layer_start_times = {}
        self._agent_request_id = None
        self._pipeline_request_id = None
        self._step_request_id = None
        self._command_request_id = None
        self._current_layer = None
        self._current_component = None
        self._current_extend_request_id = None
    
    # ==================== 内部方法 ====================
    
    def _build_request_id(self, layer: LayerType) -> str:
        """
        构建请求ID
        
        双字段设计：
        - request_id（标准）: {trace_id}:{agent_component}
        - extend_request_id（扩展）: {trace_id}:{agent}:{pipeline}:{step}:{command}
        
        格式: {trace_id}:{layer}:{component}:{parent}
        """
        if layer == LayerType.AGENT:
            return f"{self.trace_id}:{layer.value}:{self.agent_component}:root"
        
        parent = self._get_parent_component(layer)
        component = self._current_component or "unknown"
        return f"{self.trace_id}:{layer.value}:{component}:{parent}"
    
    def _get_parent_component(self, layer: LayerType) -> str:
        """获取父级组件标识"""
        if layer == LayerType.PIPELINE:
            return self.agent_component
        if layer == LayerType.STEP:
            return self._current_component or "unknown"
        if layer == LayerType.COMMAND:
            return self._current_component or "unknown"
        return "root"
    
    def _get_parent_request_id(self, layer: LayerType) -> Optional[str]:
        """获取父级请求ID（用于扩展ID构建）"""
        if layer == LayerType.AGENT:
            return None
        if layer == LayerType.PIPELINE:
            return self._agent_request_id
        if layer == LayerType.STEP:
            return self._pipeline_request_id
        if layer == LayerType.COMMAND:
            return self._step_request_id
        return None
    
    def _start(self, layer: LayerType, component: str, message: str) -> AuditEvent:
        """开始审计事件"""
        start_time = datetime.now()
        self._layer_start_times[layer] = start_time
        
        # 获取当前扩展请求ID（已由各层start方法设置）
        extend_request_id = self._current_extend_request_id or ""
        
        event = AuditEvent(
            request_id=self._base_request_id or "",
            extend_request_id=extend_request_id,
            trace_id=self.trace_id,
            session_id=self.session_id,
            layer=layer.value,
            component=component,
            parent_component=self._get_parent_component(layer),
            status=AuditStatus.START,
            timestamp=start_time.isoformat(),
            message=message or f"{layer.value}开始执行: {component}"
        )
        
        self._current_event = event
        return event
    
    def _success(self, message: str) -> AuditEvent:
        """成功结束当前层级"""
        if not self._current_event or self._current_layer is None:
            raise RuntimeError("没有进行中的审计事件")
        
        end_time = datetime.now()
        start_time = self._layer_start_times.get(self._current_layer)
        duration_ms = None
        if start_time:
            duration_ms = (end_time - start_time).total_seconds() * 1000
        
        self._current_event.status = AuditStatus.SUCCESS
        self._current_event.timestamp = end_time.isoformat()
        self._current_event.duration_ms = duration_ms
        self._current_event.message = message or f"{self._current_layer.value}执行成功"
        
        # 计算审计链哈希
        self._current_event.previous_hash = self._last_hash
        self._current_event.hash = self._calculate_hash(self._current_event)
        self._last_hash = self._current_event.hash
        
        # 添加到审计链
        self._events.append(self._current_event)
        
        # 清理当前事件
        final_event = self._current_event
        self._current_event = None
        self._layer_start_times.pop(self._current_layer, None)
        
        return final_event
    
    def _error(self, error_message: str) -> AuditEvent:
        """错误结束当前层级"""
        if not self._current_event or self._current_layer is None:
            raise RuntimeError("没有进行中的审计事件")
        
        end_time = datetime.now()
        start_time = self._layer_start_times.get(self._current_layer)
        duration_ms = None
        if start_time:
            duration_ms = (end_time - start_time).total_seconds() * 1000
        
        self._current_event.status = AuditStatus.ERROR
        self._current_event.timestamp = end_time.isoformat()
        self._current_event.duration_ms = duration_ms
        self._current_event.error_message = error_message
        self._current_event.message = f"{self._current_layer.value}执行失败: {error_message}"
        
        # 计算审计链哈希
        self._current_event.previous_hash = self._last_hash
        self._current_event.hash = self._calculate_hash(self._current_event)
        self._last_hash = self._current_event.hash
        
        # 添加到审计链
        self._events.append(self._current_event)
        
        # 清理当前事件
        final_event = self._current_event
        self._current_event = None
        self._layer_start_times.pop(self._current_layer, None)
        
        return final_event
    
    def _calculate_hash(self, event: AuditEvent) -> str:
        """计算审计事件哈希"""
        content = (
            f"{event.previous_hash}|"
            f"{event.request_id}|"
            f"{event.extend_request_id}|"
            f"{event.status.value}|"
            f"{event.timestamp}"
        )
        if event.duration_ms:
            content += f"|{event.duration_ms}"
        if event.error_message:
            content += f"|{event.error_message}"
        
        # HMAC签名
        signature = hmac.new(
            self.secret_key.encode(),
            content.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hashlib.sha256(f"{content}|{signature}".encode()).hexdigest()
    
    def _serialize(self, data: Any) -> Dict[str, Any]:
        """序列化数据为可存储格式"""
        if data is None:
            return {"type": "null", "value": None}
        
        if isinstance(data, (str, int, float, bool)):
            return {"type": type(data).__name__, "value": data}
        
        if isinstance(data, dict):
            # 限制深度，避免过大
            return {"type": "dict", "keys": list(data.keys())[:10]}
        
        if isinstance(data, (list, tuple)):
            return {"type": "list", "length": len(data)}
        
        return {"type": type(data).__name__, "value": str(data)[:200]}
    
    def _generate_trace_id(self) -> str:
        """生成追踪ID"""
        return f"trace_{uuid.uuid4().hex[:12]}"
    
    def _generate_event_id(self) -> str:
        """生成事件ID"""
        return f"evt_{uuid.uuid4().hex[:8]}"


# ==================== 集成辅助 ====================

def create_trace_context(
    session_id: str,
    agent_component: str,
    trace_id: Optional[str] = None,
    secret_key: Optional[str] = None
) -> TraceContext:
    """
    创建审计上下文的工厂方法
    
    由全局上下文调用，创建独立的审计上下文实例
    """
    return TraceContext(
        session_id=session_id,
        agent_component=agent_component,
        trace_id=trace_id,
        secret_key=secret_key
    )


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例：由全局上下文创建并使用
    def execute_agent_task(session_id: str, task: str):
        # 全局上下文创建TraceContext
        trace = create_trace_context(
            session_id=session_id,
            agent_component="comment_agent"
        )
        
        # Agent层
        trace.start_agent(f"开始执行任务: {task}")
        trace.set_input_snapshot({"task": task, "language": "java"})
        
        try:
            # Pipeline层
            trace.start_pipeline("comment_pipeline")
            
            # Step层
            trace.start_step("java_generate")
            trace.set_tag("model", "qwen_0.5b")
            
            # Command层
            trace.start_command("generate")
            trace.set_output_snapshot({"comments_generated": 15})
            trace.success_command("生成成功")
            
            trace.success_step()
            trace.success_pipeline()
            trace.success_agent("任务完成")
            
        except Exception as e:
            trace.error_agent(str(e))
        
        return trace
    
    # 使用
    trace = execute_agent_task("session_001", "生成代码注释")
    
    # 输出审计结果
    print("=== 审计统计 ===")
    print(json.dumps(trace.get_statistics(), indent=2))
    
    print("\n=== 审计链 ===")
    print(trace.export_audit_chain())
    
    print(f"\n=== 完整性验证 ===")
    print(f"审计链完整: {trace.verify_chain_integrity()}")
    
    print(f"\n=== 双字段示例 ===")
    print(f"标准request_id: {trace.get_base_request_id()}")
    print(f"扩展request_id: {trace.get_current_request_id()}")