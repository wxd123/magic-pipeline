# packages/comment/src/magicc_comment/pipeline/command_executor.py

from magic_pipeline.constant.pipeline import PIPELINE_PROJECT_CODE
from magic_pipeline.context.context import PipelineContext
from magic_pipeline.core.scope.step_scope import StepScope
from magic_base.protocol.pipeline import CommandConfig
from magic_base.protocol import Result
from magic_base.protocol.pipeline import Command
from magic_base import ApplicationContext


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

        self.set_path()

    def set_path(self): 

        # print(f"Setting paths for command: {self.cmd_config.command}")
        _pipeline_context = ApplicationContext[PipelineContext].get_context(PIPELINE_PROJECT_CODE) 
        _pipeline_config = _pipeline_context.pipeline_config  
        work_dir = _pipeline_config.project.work_path
        
        
        # print(f"{self.cmd_config.command} Initial work_dir: {work_dir}")
        # 如果命令配置中指定了模型，则输出目录包含模型名称；否则直接使用输出目录
        if self.cmd_config.model:
            output_dir = f"{work_dir}/{self.cmd_config.output_dir}/{self.cmd_config.model}"            
        else:
            output_dir = f"{work_dir}/{self.cmd_config.output_dir}"

        source_dir = f"{work_dir}/{self.cmd_config.source_dir}"

        # print(f"{self.cmd_config.command} Initial output_dir: {output_dir}")
        # print(f"{self.cmd_config.command} Initial source_dir: {source_dir}")
        self.cmd_config.output_dir = output_dir
        self.cmd_config.source_dir = source_dir
        # 如果命令配置中指定了源目录，根据源目录是绝对目录还是相对目录，设置源目录路径；否则保持源目录不变
        
        
        
           
    
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
        
        
        # print(f"Executing command: {type(cmd)}")
        if issubclass(cmd, Command):
            # print(f"Executing command: {cmd.name}")
            
            cmd_instance = cmd()
            # print(f"Executing Command type: {type(cmd_instance)}")
            return cmd_instance.execute(self.cmd_config)
        else:
            print(f"Invalid command type for {self.cmd_config.command}")
            return Result.error( "error_code", f"Invalid command type for {self.cmd_config.command}")
    
    
    