# magic_pipeline/context/step_context.py

from typing import List, Dict, Optional, Any
from magic_pipeline.core.step.step import BaseStep


class StepContext:
    """步骤上下文 - 负责存储和管理 step 序列"""
    
    def __init__(self):
        self._steps: List[BaseStep] = []           # 步骤列表（有序）
        self._step_map: Dict[str, BaseStep] = {}   # step_id -> step 映射
        self._current_index: int = -1              # 当前执行位置
    
    def add_step(self, step: BaseStep) -> None:
        """添加步骤到序列末尾"""
        self._steps.append(step)
        self._step_map[step.step_id] = step
    
    def add_steps(self, steps: List[BaseStep]) -> None:
        """批量添加步骤"""
        for step in steps:
            self.add_step(step)
    
    def get_step(self, step_id: str) -> Optional[BaseStep]:
        """根据 ID 获取步骤"""
        return self._step_map.get(step_id)
    
    def get_step_by_index(self, index: int) -> Optional[BaseStep]:
        """根据索引获取步骤"""
        if 0 <= index < len(self._steps):
            return self._steps[index]
        return None
    
    def get_all_steps(self) -> List[BaseStep]:
        """获取所有步骤（按顺序）"""
        return self._steps.copy()
    
    def get_next_step(self) -> Optional[BaseStep]:
        """获取下一个待执行的步骤"""
        next_index = self._current_index + 1
        if next_index < len(self._steps):
            return self._steps[next_index]
        return None
    
    def move_to_next(self) -> None:
        """移动到下一个步骤"""
        if self._current_index + 1 < len(self._steps):
            self._current_index += 1
    
    def get_current_step(self) -> Optional[BaseStep]:
        """获取当前正在执行的步骤"""
        if 0 <= self._current_index < len(self._steps):
            return self._steps[self._current_index]
        return None
    
    def get_step_count(self) -> int:
        """获取步骤总数"""
        return len(self._steps)
    
    def has_next(self) -> bool:
        """是否还有下一个步骤"""
        return self._current_index + 1 < len(self._steps)
    
    def reset(self) -> None:
        """重置执行位置"""
        self._current_index = -1
    
    def get_dependencies(self, step_id: str) -> List[str]:
        """获取指定步骤的依赖列表"""
        step = self._step_map.get(step_id)
        return step.depends_on if step else []
    
    def get_dependents(self, step_id: str) -> List[str]:
        """获取依赖指定步骤的所有步骤"""
        dependents = []
        for step in self._steps:
            if step_id in step.depends_on:
                dependents.append(step.step_id)
        return dependents