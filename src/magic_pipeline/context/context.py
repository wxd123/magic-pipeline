# shared/context.py
from typing import Any, Dict, Optional

from magic_base.context.application_context import ApplicationContext
from magic_base import   MagicDatabaseConfig, MagicDatabaseManager
from .command_context import CommandContext
from .node_context import NodeContext
# 各模块的类定义


class PipelineContext:
    node_context: Optional[NodeContext] = None
    command_context : Optional[CommandContext] = None

class MagicPipelineContext():

    _project_name = 'pipeline'
    
    @classmethod
    def init_context(cls, db_config=None, db_manager=None):        

        if db_config is None:
            db_config = MagicDatabaseConfig()
        if db_manager is None:
            db_manager = MagicDatabaseManager(db_config)
        ApplicationContext.initialize(cls._project_name,db_config, db_manager, PipelineContext())
    


