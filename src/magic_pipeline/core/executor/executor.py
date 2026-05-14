# packages/comment/src/magicc_comment/pipeline/executor.py
import copy
from pathlib import Path
from typing import Dict, Any, List, Optional
from magic_pipeline.context.context import PipelineContextConfig
from magic_pipeline.result import Result
from .command_executor import CommandExecutor
from magic_pipeline.core.command import Command
from magic_pipeline.context import MagicPipelineContext, StepContext, CommandContext
from magic_pipeline.utils.loader import validate_config, get_config_files, get_work_dir
class PipelineExecutor:
    """
    Pipeline 执行器，负责协调整个注释生成流程。
    
    该执行器专门为 Java 代码注释生成场景设计，支持从配置文件中加载
    Pipeline 定义，按顺序执行命令（如 clean、generate、report），
    并自动管理多模型资源的分配与释放。
    
    主要功能:
        1. 根据配置初始化执行环境
        2. 注册指定语言的命令
        3. 按顺序执行 Pipeline 中定义的步骤
        4. 自动释放模型资源（无论成功或失败）
    
    示例(pipeline.yaml): 
        ```yaml
        name: "comment-generation-pipeline"
        language: "java"
        
        # 模型池配置
        models:
          qwen_0.5b:
            provider: ollama
            name: qwen2.5-coder:0.5b
            temperature: 0.1
            
        # Pipeline 步骤定义
        pipeline:
        - command: java:clean          # 清理步骤
        - command: java:generate        # 生成步骤，可指定多个模型
            models: ["qwen_0.5b", "qwen_1.5b"]
        - command: java:report          # 报告步骤
        ```
    
    注意:
        执行完成后会自动调用 _release_resources() 释放模型资源
        即使发生异常也会执行资源清理
        generate 步骤的 models 字段为可选，未指定则使用命令默认模型
    """
    
    def __init__(self, args: Dict[str, Any], cmd_list: List[Command]):
        """
        初始化 Pipeline 执行器。

        根据配置设置语言环境，注册对应语言的命令，并初始化命令执行器。

        Args:
            args: 传入参数，pipeline或config-path必须至少包含一项：
                - project.language: 编程语言标识（如 "java", "python"），默认为 "java"
                - project.name: 项目名称
                - project.code: 项目代码
                - project.version: 项目版本(工具维护的版本，非代码版本)
                - models: 模型池配置字典，定义可用模型及其参数
                - pipeline: Pipeline 步骤列表，每个步骤为包含 command 字段的字典
        
        示例:
            config = {
                “project”:
                    "name": "test java comment"
                    "code": "comment"
                    "description": "pipeline for java comment generation"
                    "version": "1.0.0"
                    "language": "java",
                    "source_path": "source/path/of/java/project"
                "models": {
                    "qwen_0.5b": {
                        "provider": "ollama",
                        "name": "qwen2.5-coder:0.5b",
                        "temperature": 0.1
                    }
                    ...                
                },
                "pipeline": [
                    {"command": "java:clean"},
                    {"command": "java:generate", "models": ["qwen_0.5b"]},
                    {"command": "java:report"},
                    ... 
                ]
            }
            executor = PipelineExecutor(config)            
        """
        self.config = args      
        
        
        MagicPipelineContext.init_context()

        # 注册命令
        _command_context: CommandContext = MagicPipelineContext.get_command_context()
        _command_context.register_list(cmd_list)

        self.setup_context(args,cmd_list);

    def setup_context(self,args, config, cmd_list) -> bool:
        """设置 Pipeline 上下文"""

        is_valide = validate_config(args)

        # 初始化命令执行器
        if is_valide:
            config, prompt = get_config_files(args)
            models_config=config.get("models", {})
            project_config = config.get("project", {})
            work_dir = get_work_dir(project_config)

            #ctx_command = CommandExecutor(models_config)

            # 初始化命令上下文
            ctx_command: CommandContext = CommandContext()
            ctx_command.register_list(cmd_list)

            # 初始化step上下文            
            ctx_step = StepContext(config)        
            ctx_step.set("work_dir", work_dir)  # 统一使用 work_dir

            # 初始化pipeline上下文
            pipeline_config = PipelineContextConfig()
            pipeline_config.step_context = ctx_step
            pipeline_config.cmd_context = ctx_command
            MagicPipelineContext.init_context(pipeline_config)
            return True
        else:
            print(f"参数验证失败，退出pipeline执行.")
            return False
        
    
    def get_step_context()->StepContext:
        return MagicPipelineContext.get_step_context()
    
    
    def run(self,pipeline_name: Optional[str]) -> Result:
        """    
        从配置中获取 Pipeline 步骤列表，按顺序执行每个步骤。
        步骤格式支持两种形式：
            - 字符串格式（向后兼容）: "java:clean"
            - 字典格式（推荐）: {"command": "java:generate", "models": ["qwen_0.5b"]}
        
        如果任何步骤执行失败，立即返回失败结果，不再执行后续步骤。
        无论执行成功还是失败，最终都会释放模型资源。        
        Args:
            pipeline_name: pipeline 名称
        
        Returns:
            Result 对象:
                - 成功: Result.ok(message="Pipeline completed")
                - 失败: Result.fail(message="错误描述")
        
        示例:
            >>> # 使用默认 pipeline 名称
            >>> result = executor.run(ctx)
            
            >>> # 检查执行结果
            >>> if not result.success:
            ...     print(f"Pipeline 执行失败: {result.message}")
        
        注意:
            - 方法使用 finally 块确保资源被正确释放
            - 多模型配置会在 generate 步骤中依次使用每个模型
        """
        try:
            # 获取 pipeline 配置
            step_context:StepContext = MagicPipelineContext.get_step_context()

            if pipeline_name:
                project_config = step_context.get('project', {})
                if not project_config.name:
                    return Result.fail(f"pipeline '{pipeline_name}' not found")
            
            # 执行 pipeline 中的每个步骤
            pipeline = step_context.get('pipeline',{})
            for step in pipeline:              

                command_executor = CommandExecutor(step)
                result = command_executor.execute_step(step)
                if not result.success:
                    return result
            
            return Result.ok(message="Pipeline completed")
        
        finally:
            # 无论成功还是失败，都释放模型资源
            self._release_resources()
    
    def _release_resources(self):
        """
        释放模型资源（内部方法）。
        
        释放命令执行器中占用的所有模型资源，如 LLM 连接、缓存等。
        此方法会在 run 方法的 finally 块中自动调用。
        
        资源释放包括:
            - 关闭 LLM 客户端连接
            - 清理临时文件
            - 释放内存中的模型缓存
        
        示例输出:
            ============================================================
            Pipeline 执行结束，释放模型资源...
        
        注意:
            仅在命令执行器实现了 release_resources 方法时才会执行释放操作。
            如果没有实现该方法，跳过释放步骤（不报错）。
        """
        if hasattr(self.command_executor, 'release_resources'):
            print("\n" + "="*60)
            print("Pipeline 执行结束，释放模型资源...")
            self.command_executor.release_resources()