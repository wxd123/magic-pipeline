# packages/comment/src/magicc_comment/pipeline/command_executor.py

from magic_pipeline.core.scope.step_scope import StepScope
from magic_tool.pipeline import Result, CommandConfig
from magic_pipeline.core.command import Command

class CommandExecutor:
    """负责执行 pipeline 中的命令"""
    
    def __init__(self, cmd_config: CommandConfig, scope: StepScope):
        """
        初始化命令执行器
        
        Args:
            cmd_config: 命令配置
            scope:      步骤作用域
        """
        self.cmd_config = cmd_config       
        
        self.scope = scope
        
        
    
    def execute(self) -> Result:
        """
        执行单个步骤
        
        Args:            
            step: 步骤配置字典，必须包含 "command" 字段，可选包含 "models"、"model_ref"、"description" 等
            
        Returns:
            Result: 执行结果，成功时包含执行数据，失败时包含错误信息
            
        Note:
            支持两种命令类型：
            1. LLMCommand: 需要调用大语言模型执行的命令，支持多模型依次执行
            2. 普通命令: 不需要 LLM 的常规命令，直接执行
        """
        
        if not self.cmd_config:
            return Result.fail("Missing command")

        cmd:Command = self.scope.require_cmd(self.cmd_config.command)
        
        
        if not cmd:
            return Result.fail(f"Command not found: {self.cmd_config.command}")
        
        

        if isinstance(cmd, Command):
            return cmd.execute(self.scope)
        else:
            print(f"Invalid command type for {self.cmd_config.command}")
            return None
    
    
    