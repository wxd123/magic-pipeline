# magic_pipeline/context/step_context.py
"""
步骤上下文管理模块

提供 Pipeline 执行过程中的上下文管理功能，包括配置访问和运行时变量存储。
"""

from typing import Any, Dict, List, Optional

from magic_pipeline.core.model.pipeline_yaml import PipelineConfig
from magic_pipeline.core.model.step.step_yaml import Step


class StepContext:
    """
    步骤上下文管理器
    
    该类管理 Pipeline 执行过程中的两个核心数据：
        1. 配置信息：从 PipelineConfig 中提取的 pipeline 步骤列表（只读）
        2. 运行时变量：当前正在执行的 Step 对象（动态更新）
    
    设计原则：
        - 配置数据：从 PipelineConfig.pipeline 获取步骤列表，初始化后不变
        - 运行时数据：存储当前执行的 Step 对象，支持动态更新
        - 保持现有 API：config、get_runtime、set_runtime、clear_runtime
    
    业务场景:
        - 获取 Pipeline 步骤列表: ctx.config
        - 获取当前执行的步骤: ctx.get_runtime()
        - 设置当前执行的步骤: ctx.set_runtime(step)
        - 清空当前步骤: ctx.clear_runtime()
    
    示例:
        >>> config = PipelineConfig.from_yaml('pipeline.yaml')
        >>> ctx = StepContext(config)
        >>> current_step = CommandStep(command="java:comment:clean")
        >>> ctx.set_runtime(current_step)
        >>> ctx.get_runtime()
        CommandStep(command="java:comment:clean")
        >>> ctx.config  # 获取完整的步骤列表
        [CommandStep(...), LoopStep(...), ...]
    """
    
    def __init__(self, data: Optional[PipelineConfig] = None):
        """
        初始化上下文对象
        
        Args:
            data: PipelineConfig 配置对象，若为 None 则初始化为空上下文
        
        注意:
            参数名保留为 data，实际应为 PipelineConfig 对象
            初始化时会从 data.pipeline 提取步骤列表作为只读配置
        """
        # 持有原始配置对象中的 pipeline 步骤列表，保持完整性和类型安全
        # 用于获取 Pipeline 定义的所有步骤（只读）
        self._config: Optional[List[Step]] = data.pipeline if data else None

        # 运行时变量：存储当前正在执行的 Step 对象
        # 用于在 Pipeline 执行过程中传递当前步骤信息
        self._runtime_vars: Optional[Step] = None

    @property
    def config(self) -> Optional[List[Step]]:
        """
        获取 Pipeline 步骤列表配置
        
        提供对原始 PipelineConfig.pipeline 步骤列表的直接访问，
        用于需要遍历或查询步骤定义信息的场景。
        
        Returns:
            Pipeline 步骤列表（List[Step]），如果未初始化则返回 None
        
        示例:
            >>> ctx = StepContext(config)
            >>> for step in ctx.config:
            ...     print(type(step))
            <class 'CommandStep'>
            <class 'LoopStep'>
        """
        return self._config
    
    def get_runtime(self) -> Step:
        """
        获取当前运行的步骤对象
        
        从运行时变量中获取当前正在执行的 Step 实例，
        用于在 Pipeline 执行过程中获取当前步骤的信息。
        
        Returns:
            当前正在执行的 Step 对象，未设置时返回 None
        
        示例:
            >>> current = ctx.get_runtime()
            >>> if current:
            ...     print(f"正在执行: {current.command}")
        """
        return self._runtime_vars
    
    def set_runtime(self, step: Step) -> bool:
        """
        设置当前运行的步骤对象
        
        在 Pipeline 执行过程中，当开始执行某个步骤时调用此方法，
        将当前步骤存储到运行时变量中。
        
        Args:
            step: 要设置的 Step 对象，不能为 None
        
        Returns:
            bool: 设置成功返回 True，step 为空时返回 False
        
        示例:
            >>> step = CommandStep(command="java:comment:generate")
            >>> if ctx.set_runtime(step):
            ...     print("步骤已设置")
        """
        if step is None:
            print(f"警告: 运行时变量设置失败: step 不能为空")
            return False
        
        self._runtime_vars = step
        return True
    
    def clear_runtime(self) -> bool:
        """
        清空当前运行的步骤对象
        
        在 Pipeline 步骤执行完成后调用此方法，清空运行时变量。
        通常与 set_runtime 配对使用，确保上下文状态干净。
        
        Returns:
            bool: 始终返回 True，表示清空操作成功
        
        示例:
            >>> ctx.set_runtime(step)
            >>> ctx.get_runtime() is not None
            True
            >>> ctx.clear_runtime()
            >>> ctx.get_runtime() is None
            True
        """
        self._runtime_vars = None
        self._data = None
        return True


class MagicStepContext(StepContext):
    """
    Magic Pipeline 步骤上下文扩展类
    
    继承自 StepContext，用于 Magic Pipeline 特定的上下文管理需求。
    目前保持与父类相同的功能，未来可扩展特定于 Magic Pipeline 的功能。
    
    使用场景:
        当需要为 Magic Pipeline 添加额外功能（如步骤执行统计、
        性能监控、日志记录等）时，可在此类中扩展。
    """
    pass