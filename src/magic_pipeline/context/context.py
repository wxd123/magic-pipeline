# shared/context.py
from typing import Any, Dict, Optional

from magic_base.context.application_context import ApplicationContext
from magic_base import   MagicDatabaseConfig, MagicDatabaseManager
from .command_context import CommandContext
from .step_context import StepContext
from magic_pipeline.constant import PIPELINE_PROJECT_CODE

# 各模块的类定义


class PipelineContext:
    step_context: Optional[StepContext] = None
    command_context : Optional[CommandContext] = None   

class MagicPipelineContext():

    
    
    @classmethod
    def init_context(cls, db_config=None, db_manager=None):        

        _pipeLine_context = PipelineContext()
        _pipeLine_context.step_context = StepContext()
        _pipeLine_context.command_context = CommandContext()
        if db_config is None:
            db_config = MagicDatabaseConfig()
        if db_manager is None:
            db_manager = MagicDatabaseManager(db_config)
        ApplicationContext.initialize(PIPELINE_PROJECT_CODE,db_config, db_manager, _pipeLine_context)

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
    


