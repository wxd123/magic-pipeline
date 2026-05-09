# magic_pipeline/core/command/step.py
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime


class StepStatus(Enum):
    """步骤执行状态枚举"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 执行中
    SUCCESS = "success"      # 执行成功
    FAILED = "failed"        # 执行失败
    SKIPPED = "skipped"      # 跳过（依赖失败导致）


class BaseStep:
    """
    步骤基类 - 表示流水线中的一个执行单元
    
    步骤是流水线的最小执行单位，包含命令类型、参数、依赖关系和执行状态。
    步骤不包含具体执行逻辑，执行逻辑由对应的 Command 类实现。
    
    属性:
        step_id: 步骤唯一标识符，在同一流水线中必须唯一
        command: 命令类型标识符，对应注册的 Command 类（如 "read_csv", "subflow"）
        params: 命令参数字典，传递给 Command 执行时使用
        depends_on: 依赖的步骤 ID 列表，当前步骤会等待所有依赖步骤成功后才能执行
        
        status: 当前步骤的执行状态，使用 StepStatus 枚举
        result: 步骤执行结果，由 Command 返回的数据
        error: 执行失败时的错误信息
        start_time: 步骤开始执行的时间戳
        end_time: 步骤执行完成的时间戳
    """
    
    def __init__(
        self,
        step_id: str,
        command: str,
        params: Optional[Dict[str, Any]] = None,
        depends_on: Optional[List[str]] = None
    ):
        """
        初始化步骤实例
        
        Args:
            step_id: 步骤唯一标识符
            command: 命令类型标识符
            params: 命令参数字典，默认为空字典
            depends_on: 依赖的步骤 ID 列表，默认为空列表
        """
        self.step_id = step_id
        """步骤唯一标识符"""
        
        self.command = command
        """命令类型标识符"""
        
        self.params = params or {}
        """命令参数字典"""
        
        self.depends_on = depends_on or []
        """依赖的步骤 ID 列表"""
        
        # 运行时状态
        self.status = StepStatus.PENDING
        """当前执行状态，默认为 PENDING"""
        
        self.result: Optional[Any] = None
        """执行结果数据"""
        
        self.error: Optional[str] = None
        """错误信息（仅在 FAILED 时有效）"""
        
        self.start_time: Optional[datetime] = None
        """开始执行时间"""
        
        self.end_time: Optional[datetime] = None
        """执行完成时间"""
    
    def is_ready(self) -> bool:
        """
        检查步骤是否准备好执行
        
        步骤需要满足以下条件才算就绪：
        1. 状态为 PENDING
        2. 所有依赖步骤都已成功执行
        
        注意：此方法需要外部提供依赖步骤的状态查询，通常由 StepContext 实现。
        此处仅作为接口定义，实际逻辑由调度器实现。
        
        Returns:
            步骤是否准备好执行
        """
        return self.status == StepStatus.PENDING
    
    def is_completed(self) -> bool:
        """检查步骤是否已完成（成功或失败）"""
        return self.status in [StepStatus.SUCCESS, StepStatus.FAILED, StepStatus.SKIPPED]
    
    def mark_running(self) -> None:
        """标记步骤为执行中，并记录开始时间"""
        self.status = StepStatus.RUNNING
        self.start_time = datetime.now()
    
    def mark_success(self, result: Any = None) -> None:
        """
        标记步骤执行成功
        
        Args:
            result: 执行结果数据
        """
        self.status = StepStatus.SUCCESS
        self.result = result
        self.end_time = datetime.now()
    
    def mark_failed(self, error: str) -> None:
        """
        标记步骤执行失败
        
        Args:
            error: 错误信息
        """
        self.status = StepStatus.FAILED
        self.error = error
        self.end_time = datetime.now()
    
    def mark_skipped(self, reason: str = "") -> None:
        """
        标记步骤为跳过
        
        通常用于依赖步骤失败时，跳过当前步骤
        
        Args:
            reason: 跳过原因
        """
        self.status = StepStatus.SKIPPED
        self.error = reason if reason else "Dependency failed"
        self.end_time = datetime.now()
    
    def get_duration(self) -> Optional[float]:
        """
        获取步骤执行耗时（秒）
        
        Returns:
            执行耗时，如果尚未开始或未完成则返回 None
        """
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def __repr__(self) -> str:
        return f"BaseStep(id={self.step_id}, command={self.command}, status={self.status.value})"