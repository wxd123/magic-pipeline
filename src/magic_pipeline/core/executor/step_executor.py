

from magic_pipeline.core.scope.step_scope import StepScope
from magic_pipeline.core.model import CommandConfig, LoopConfig
from magic_pipeline.core.command import CommandExecutor
from magic_pipeline.result.result import Result

class StepExecutor:
    """步骤执行器 - 负责执行单个步骤的逻辑"""
    
    def __init__(self, step):
        self.step = step
        self.scope = StepScope(step.name)
    
    def run(self) -> Result:
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
            

            step = self.step
            if step.loop:
                return self.run_loop(step.loop)
            
            if step.command:   
                return self.run_command(step.command)            
        
        finally:
            # 无论成功还是失败，都释放模型资源
            self._release_resources()

    def run_command(self, cmd: CommandConfig) -> Result:
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
            step_scope: StepScope = StepScope(cmd.model)
            is_valid = step_scope.require_model(cmd.model)
            executor = CommandExecutor(cmd, step_scope)
            result = executor.execute()
            if not result.success:
                return result
            
            return Result.ok(message="Pipeline completed")
        
        finally:
            # 无论成功还是失败，都释放模型资源
            self._release_resources()

    def run_loop(self, loops: LoopConfig) -> Result:
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
            
            for model in loops.models:              
                step_scope: StepScope = StepScope(loops.id)
                is_valid = step_scope.require_model(model.get('id'))

                if is_valid:
                    print(f"模型 '{model.get('id')}' 可用，开始执行循环步骤")
                    for step in loops.steps:
                        command_executor = CommandExecutor(step, step_scope)
                        result = command_executor.execute()
                        if not result.success:
                            return result
            
            return Result.ok(message="Pipeline loop completed")
        
        finally:
            # 无论成功还是失败，都释放模型资源
            self._release_resources()