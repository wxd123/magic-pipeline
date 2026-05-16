# shared/context.py
from dataclasses import dataclass
from typing import Any, Dict, Optional

from magic_base.context.application_context import ApplicationContext
from magic_base import   BaseDatabaseConfig, BaseDatabaseManager, MagicDatabaseConfig, MagicDatabaseManager
from .command_context import CommandContext
from .step_context import StepContext
from magic_pipeline.constant import PIPELINE_PROJECT_CODE
from .model_context import ModelContext
# 各模块的类定义

@dataclass
class PipelineContextConfig:
    """
    管道上下文初始化配置类
    
    用于配置 PipelineContext 初始化时所需的各个子上下文组件和数据库组件。
    所有字段均为可选，未提供时会使用默认值。
    
    Attributes:
        db_config: 数据库配置对象，默认使用 MagicDatabaseConfig()
        db_manager: 数据库管理器对象，默认使用 MagicDatabaseManager(db_config)
        step_context: 步骤上下文对象，默认使用 StepContext()
        cmd_context: 命令上下文对象，默认使用 CommandContext()
        model_context: 模型上下文对象，默认使用 ModelContext([])
    """
    db_config: Optional[BaseDatabaseConfig] = None
    db_manager: Optional[BaseDatabaseManager] = None
    step_context: Optional[StepContext] = None
    cmd_context: Optional[CommandContext] = None
    model_context: Optional[ModelContext] = None

    
class PipelineContext:
    """
    管道上下文容器类
    
    作为步骤上下文、命令上下文和模型上下文的聚合容器，
    统一管理管道执行过程中所需的各种上下文对象。
    
    Attributes:
        step_context: 步骤上下文，管理步骤执行相关的状态和数据
        command_context: 命令上下文，管理命令执行相关的状态和数据
        model_context: 模型上下文，管理模型相关的实例和配置
    """
    step_context: Optional[StepContext] = None
    command_context : Optional[CommandContext] = None
    model_context: Optional[ModelContext] = None


class MagicPipelineContext():
    """
    魔法管道上下文管理类（单例模式）
    
    提供管道上下文的全局初始化和访问接口。通过 ApplicationContext 进行统一管理，
    使用 PIPELINE_PROJECT_CODE 作为项目标识符。所有方法均为类方法，无需实例化。
    
    功能：
        1. 初始化全局管道上下文及相关数据库组件
        2. 提供对 StepContext 的获取和设置
        3. 提供对 CommandContext 的获取和设置
        4. 提供对 ModelContext 的获取和设置
    
    使用示例：
        # 初始化上下文（使用默认配置）
        MagicPipelineContext.init_context()
        
        # 使用自定义配置初始化
        config = PipelineContextConfig(step_context=custom_step_context)
        MagicPipelineContext.init_context(config)
        
        # 获取步骤上下文
        step_ctx = MagicPipelineContext.get_step_context()
        
        # 设置命令上下文
        cmd_ctx = CommandContext()
        MagicPipelineContext.set_command_context(cmd_ctx)
    """
    
    @classmethod
    def init_context(cls, context_config:Optional[PipelineContextConfig]=None):
        """
        初始化全局管道上下文
        
        创建并初始化 PipelineContext 实例，配置数据库组件，并注册到 ApplicationContext 中。
        如果未提供配置对象，将使用默认配置。
        
        Args:
            context_config: 管道上下文配置对象，为 None 时使用 PipelineContextConfig() 默认配置
        """
        context_config = context_config or PipelineContextConfig()
        
        # 初始化 PipelineContext并
        _pipeline_context = PipelineContext()
        _pipeline_context.step_context = context_config.step_context or StepContext()
        _pipeline_context.command_context = context_config.cmd_context or CommandContext()   
        _pipeline_context.model_context = context_config.model_context or ModelContext([])

        # 初始化数据库配置和管理器
        db_config = context_config.db_config or MagicDatabaseConfig()        
        db_manager = context_config.db_manager or MagicDatabaseManager(db_config)

        # 注册到 ApplicationContext
        ApplicationContext.initialize(PIPELINE_PROJECT_CODE, db_config, db_manager, _pipeline_context)

    @classmethod
    def get_step_context(cls)->StepContext:
        """
        获取步骤上下文实例
        
        从全局 ApplicationContext 中获取 PipelineContext，并返回其中的 step_context。
        
        Returns:
            StepContext: 步骤上下文实例
        """
        _pipeline_context: PipelineContext = ApplicationContext[PipelineContext].get_context(PIPELINE_PROJECT_CODE)
        _step_context = _pipeline_context.step_context
        return _step_context
    
    @classmethod
    def set_step_context(cls, context: StepContext):
        """
        设置步骤上下文实例
        
        将新的步骤上下文设置到全局 PipelineContext 中。
        
        Args:
            context: 要设置的 StepContext 实例
        """
        _pipeline_context: PipelineContext = ApplicationContext[PipelineContext].get_context(PIPELINE_PROJECT_CODE)
        _pipeline_context.step_context = context        
    
    @classmethod
    def get_command_context(cls)->CommandContext:
        """
        获取命令上下文实例
        
        从全局 ApplicationContext 中获取 PipelineContext，并返回其中的 command_context。
        
        Returns:
            CommandContext: 命令上下文实例
        """
        _pipeline_context: PipelineContext = ApplicationContext[PipelineContext].get_context(PIPELINE_PROJECT_CODE)
        _command_context = _pipeline_context.command_context
        return _command_context
    
    @classmethod
    def set_command_context(cls, context: CommandContext):
        """
        设置命令上下文实例
        
        将新的命令上下文设置到全局 PipelineContext 中。
        
        Args:
            context: 要设置的 CommandContext 实例
        """
        _pipeline_context: PipelineContext = ApplicationContext[PipelineContext].get_context(PIPELINE_PROJECT_CODE)
        _pipeline_context.command_context = context

    @classmethod
    def get_model_context(cls)->ModelContext:
        """
        获取模型上下文实例
        
        从全局 ApplicationContext 中获取 PipelineContext，并返回其中的 model_context。
        
        Returns:
            ModelContext: 模型上下文实例
        """
        _pipeline_context: PipelineContext = ApplicationContext[PipelineContext].get_context(PIPELINE_PROJECT_CODE)
        _model_context = _pipeline_context.model_context
        return _model_context    

    @classmethod
    def set_model_context(cls, context: ModelContext):
        """
        设置模型上下文实例
        
        将新的模型上下文设置到全局 PipelineContext 中。
        
        Args:
            context: 要设置的 ModelContext 实例
        """
        _pipeline_context: PipelineContext = ApplicationContext[PIPELINE_PROJECT_CODE].get_context(PIPELINE_PROJECT_CODE)
        _pipeline_context.model_context = context