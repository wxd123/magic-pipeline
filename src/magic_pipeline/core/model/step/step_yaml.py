

# magic_pipeline/core/model/step/step_yaml.py
from dataclasses import dataclass
from typing import  Dict, List, Optional, Union
import uuid
from magic_base.protocol.pipeline import CommandConfig, Step






# ============ Pipeline 节点（5种） ============



@dataclass
class LoopStep(Step):
    """循环节点 - 遍历列表"""
    steps: List[Union['CommandConfig', 'LoopStep', 'ConditionStep', 'ParallelStep', 'SubPipelineStep']]
    id: Optional[str] = None            # 源目录
    name: Optional[str] = None          # 输出目录 
    type: str = "loop"                  # 循环ID，唯一标识一个循环块
    models: List[str] = None            # 可选的模型列表，适用于需要模型支持的循环    
    max_iterations: int = 100           # 最大迭代次数

    
    def __post_init__(self):

        """初始化后处理"""
        # id与name自动处理
        unique_id = uuid.uuid4().hex[:6]
        # 如果没有提供 id，自动生成
        if not self.id:
            self.id = f"{self.type}_{unique_id}"
        # 如果没有提供 name，使用 command
        if not self.name:
            self.name = f"{self.type}_{unique_id}"

@dataclass
class ConditionStep:
    """条件节点 - 简单分支"""
    on: str                                  # 检查的状态变量
    cases: Dict[str, List[Union['CommandConfig', 'LoopStep', 'ConditionStep', 'ParallelStep', 'SubPipelineStep']]]
    default: Optional[List[Union['CommandConfig', 'LoopStep', 'ConditionStep', 'ParallelStep', 'SubPipelineStep']]] = None


@dataclass
class ParallelStep:
    """并行节点 - 并行执行"""
    steps: List[Union['CommandConfig', 'LoopStep', 'ConditionStep', 'ParallelStep', 'SubPipelineStep']]
    max_concurrency: int = 3
    fail_fast: bool = True


@dataclass
class SubPipelineStep:
    """子流程节点 - 引用其他 pipeline"""
    path: str                                    # 子流程文件路径
    params: Optional[Dict[str, str]] = None     # 参数映射


# 步骤联合类型
StepDefine = Union[CommandConfig, LoopStep, ConditionStep, ParallelStep, SubPipelineStep]



