# shared/context.py
from dataclasses import dataclass
from typing import Any, Dict, Optional

from magic_base.context.application_context import ApplicationContext
from magic_base import   BaseDatabaseConfig, BaseDatabaseManager, MagicDatabaseConfig, MagicDatabaseManager
from .command_context import CommandContext
from .step_context import StepContext
from magic_pipeline.constant import PIPELINE_PROJECT_CODE

# 各模块的类定义

@dataclass
class PipelineContextConfig:
    """上下文初始化配置类"""
    db_config: Optional[BaseDatabaseConfig] = None
    db_manager: Optional[BaseDatabaseManager] = None
    step_context: Optional['StepContext'] = None
    cmd_context: Optional['CommandContext'] = None
    
class PipelineContext:
    step_context: Optional[StepContext] = None
    command_context : Optional[CommandContext] = None   

class MagicPipelineContext():

    
    
    @classmethod
    def init_context(cls, context_config:Optional[PipelineContextConfig]=None):        
        context_config = context_config or PipelineContextConfig()
        _pipeline_context = PipelineContext()
        _pipeline_context.step_context = context_config.step_context or StepContext()
        _pipeline_context.command_context = context_config.cmd_context or CommandContext()        
        db_config = context_config.db_config or MagicDatabaseConfig()        
        db_manager = context_config.db_manager or MagicDatabaseManager(db_config)
        ApplicationContext.initialize(PIPELINE_PROJECT_CODE,db_config, db_manager, _pipeline_context)

    @classmethod
    def get_step_context(cls)->StepContext:
        _pipeline_context: PipelineContext= ApplicationContext[PipelineContext].get_context(PIPELINE_PROJECT_CODE)
        _step_context = _pipeline_context.step_context
        return _step_context
    
    @classmethod
    def set_step_context(cls, context: StepContext):
        _pipeline_context: PipelineContext= ApplicationContext[PipelineContext].get_context(PIPELINE_PROJECT_CODE)
        _pipeline_context.step_context = context        
    
    @classmethod
    def get_command_context(cls)->CommandContext:
        _pipeline_context: PipelineContext= ApplicationContext[PipelineContext].get_context(PIPELINE_PROJECT_CODE)
        _command_context = _pipeline_context.command_context
        return _command_context
    


