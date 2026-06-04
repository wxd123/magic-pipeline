import copy

from magic_pipeline.core.model.step.step_yaml import Step
from magic_pipeline.core.scope.step_scope import StepScope
from magic_pipeline.core.model import LoopConfig
from .command_executor import CommandExecutor
from magic_base.protocol.pipeline import CommandConfig
from magic_base.protocol import Result
from typing import List, Optional
import uuid


class StepExecutor:
    """步骤执行器 - 负责执行单个步骤的逻辑"""
    
    def __init__(self, step: Step ):
        """
        初始化步骤执行器
        
        Args:
            step: 要执行的步骤配置
        """
        self.step = step
        self.scope = StepScope(step.name)
    
    
    
    def run(self) -> Result:
        """
        执行步骤
        
        Returns:
            Result: 统一结果信封
                - 成功: 包含步骤执行结果
                - 失败: 包含错误码和错误信息
        
        Example:
            >>> executor = StepExecutor(step)
            >>> result = executor.run()
            >>> if result.is_success:
            ...     print(f"执行成功: {result.output}")
            ... else:
            ...     print(f"执行失败: {result.error_message}")
        """
        try:
            step = self.step
            # print(f"[DEBUG] Executing step: {step}")
            
            # 步骤类型到执行方法的映射
            switch = {
                "command": self._run_command,
                "loop": self._run_loop
            }
            
            func = switch.get(step.type)
            if func:
                return func(step)
            
            # 未知步骤类型
            return Result.error(
                error_code="UNKNOWN_STEP_TYPE",
                error_message=f"未知的步骤类型: {step.type}",
                metadata={"step_type": step.type, "step_name": step.name}
            )
        
        except Exception as e:
            # 捕获未预期的异常
            return Result.error(
                error_code="STEP_EXECUTION_ERROR",
                error_message=f"步骤执行异常: {str(e)}",
                metadata={"step_name": self.step.name, "exception_type": type(e).__name__}
            )
        
        finally:
            # 无论成功还是失败，都释放模型资源
            self._release_resources()

    def _run_command(self, cmd: CommandConfig) -> Result:
        """
        执行命令步骤
        
        Args:
            cmd: 命令配置
            
        Returns:
            Result: 命令执行结果
        """
        try:
            step_scope: StepScope = StepScope(cmd.command)
            
            # 检查模型可用性
            if cmd.model:
                is_valid = step_scope.require_model(cmd.model)
                if not is_valid:
                    return Result.error(
                        error_code="MODEL_UNAVAILABLE",
                        error_message=f"模型 '{cmd.model}' 不可用，无法执行命令 '{cmd.command}'",
                        metadata={
                            "command": cmd.command,
                            "model": cmd.model,
                            "step_name": self.step.name
                        }
                    )
            # else:
            #     print(f"命令 '{cmd.command}' 不需要模型支持，直接执行")
            
            # 执行命令
            executor = CommandExecutor(cmd, step_scope)
            result = executor.execute()
            
            # 检查执行结果
            if not result.success:  # 假设 CommandExecutor 返回的对象有 success 属性
                return Result.error(
                    error_code="COMMAND_EXECUTION_FAILED",
                    error_message=result.message if hasattr(result, 'message') else "命令执行失败",
                    metadata={
                        "command": cmd.command,
                        "model": cmd.model,
                        "original_result": result
                    }
                )
            
            # 命令执行成功
            return Result.success(
                output=result.output if hasattr(result, 'output') else result,
                metadata={
                    "command": cmd.command,
                    "model": cmd.model,
                    "step_name": self.step.name
                }
            )
        
        except Exception as e:
            return Result.error(
                error_code="COMMAND_EXCEPTION",
                error_message=f"命令执行异常: {str(e)}",
                metadata={
                    "command": cmd.command,
                    "model": cmd.model,
                    "exception_type": type(e).__name__
                }
            )
        
        finally:
            self._release_resources()

    def _run_loop(self, loop: LoopConfig) -> Result:
        """
        执行循环步骤
        
        Args:
            loop: 循环配置
            
        Returns:
            Result: 循环执行结果
        """
        # print("="*60, flush=True)
        # print(f"[DEBUG] 进入 _run_loop", flush=True)
        # print(f"[DEBUG] loop.id: {loop.id}", flush=True)
        # print(f"[DEBUG] loop.type: {loop.type}", flush=True)
        # print(f"[DEBUG] loop.models: {loop.models}", flush=True)
        # print(f"[DEBUG] loop.steps: {loop.steps}", flush=True)
        # print(f"[DEBUG] loop.max_iterations: {loop.max_iterations}", flush=True)
        # print("="*60, flush=True)
        
        try:
            step_scope: StepScope = StepScope(loop.id)
            iteration_results = []
            
            # 处理模型列表或单次执行
            if loop.models:
                print(f"开始遍历模型列表，共 {len(loop.models)} 个模型")
                
                for idx, model_id in enumerate(loop.models):
                    print(f"处理模型 {idx+1}/{len(loop.models)}: {model_id}")
                    
                    # 检查模型可用性
                    is_valid = step_scope.require_model(model_id)
                    if not is_valid:
                        print(f"模型 '{model_id}' 不可用，跳过")
                        continue
                    
                    print(f"模型 '{model_id}' 可用，开始执行循环步骤")
                    
                    # 执行步骤列表
                    result = self._execute_steps(loop.steps, step_scope, model_id, idx)
                    
                    if not result.is_success:
                        print(f"模型 {model_id} 的步骤执行失败: {result.error_message}")
                        return result
                    
                    iteration_results.append({
                        "model": model_id,
                        "iteration": idx,
                        "result": result.output
                    })
                    
                    print(f"模型 {model_id} 的所有步骤执行完成")
            else:
                print(f"循环步骤 '{loop.id}' 不需要模型支持，直接执行")
                result = self._execute_steps(loop.steps, step_scope, None, 0)
                
                if not result.is_success:
                    return result
                
                iteration_results.append({
                    "iteration": 0,
                    "result": result.output
                })
            
            print(f"run_loop 执行完成，共执行 {len(iteration_results)} 次迭代")
            
            return Result.success(
                output={
                    "loop_id": loop.id,
                    "iterations": len(iteration_results),
                    "results": iteration_results
                },
                metadata={
                    "loop_id": loop.id,
                    "models_used": loop.models,
                    "max_iterations": loop.max_iterations
                }
            )
        
        except Exception as e:
            print(f"run_loop 异常: {e}")
            import traceback
            traceback.print_exc()
            
            return Result.error(
                error_code="LOOP_EXECUTION_ERROR",
                error_message=f"循环执行异常: {str(e)}",
                metadata={
                    "loop_id": loop.id,
                    "exception_type": type(e).__name__
                }
            )

    def _execute_steps(
        self, 
        steps: List[Step], 
        step_scope: StepScope, 
        model_id: Optional[str] = None,
        iteration: int = 0
    ) -> Result:
        """
        执行步骤列表
        
        Args:
            steps: 步骤列表
            step_scope: 步骤作用域
            model_id: 当前使用的模型ID
            iteration: 当前迭代次数
            
        Returns:
            Result: 步骤执行结果
        """
        
        
        if not steps:
            print(f"[WARNING] steps 为空")
            return Result.success(
                output={"message": "没有步骤需要执行", "iteration": iteration}
            )
        
        executed_results = []
        
        for idx, step in enumerate(steps):
            # print(f"[DEBUG] --- 执行子步骤 {idx+1}/{len(steps)} ---")
            # print(f"[DEBUG] step 类型: {type(step)}")
            # print(f"[DEBUG] step 内容: {step}")
            # print(f"[DEBUG]   step id={id(step)}, source_dir={step.source_dir}")
            # 如果是命令步骤，设置模型
            if hasattr(step, 'model') and model_id:
                old_model = step.model
                step.model = model_id
                print(f"[DEBUG] 设置步骤模型: {old_model} -> {model_id}")
            
            try:
                # print(f"[DEBUG] 创建 CommandExecutor")
                _loop_step = copy.deepcopy(step)
                command_executor = CommandExecutor(_loop_step, step_scope)
                # print(f"[DEBUG] 开始执行命令")
                result = command_executor.execute()
                # print(f"[DEBUG] 命令执行完成, success: {result.success}")
                
                if not result.success:
                    error_msg = result.message if hasattr(result, 'message') else f"步骤 {idx+1} 执行失败"
                    print(f"[ERROR] {error_msg}")
                    
                    return Result.error(
                        error_code="SUB_STEP_FAILED",
                        error_message=error_msg,
                        metadata={
                            "iteration": iteration,
                            "step_index": idx,
                            "step_name": getattr(step, 'name', 'unknown'),
                            "model_id": model_id
                        }
                    )
                
                # 记录执行结果
                executed_results.append({
                    "step_index": idx,
                    "step_name": getattr(step, 'name', f'step_{idx}'),
                    "result": result.output if hasattr(result, 'output') else result
                })
                
                # print(f"[DEBUG] 步骤 {idx+1} 执行成功")
                
            except Exception as e:
                # print(f"[ERROR] 步骤 {idx+1} 执行异常: {e}")
                import traceback
                traceback.print_exc()
                
                return Result.error(
                    error_code="SUB_STEP_EXCEPTION",
                    error_message=f"步骤执行异常: {str(e)}",
                    metadata={
                        "iteration": iteration,
                        "step_index": idx,
                        "step_name": getattr(step, 'name', 'unknown'),
                        "exception_type": type(e).__name__
                    }
                )
        
        # print(f"[DEBUG] _execute_steps 所有步骤执行完成")
        
        return Result.success(
            output={
                "iteration": iteration,
                "steps_executed": len(executed_results),
                "results": executed_results
            },
            metadata={
                "iteration": iteration,
                "model_id": model_id,
                "total_steps": len(steps)
            }
        )

    def _release_resources(self):
        """
        释放模型资源（内部方法）。
        
        释放命令执行器中占用的所有模型资源，如 LLM 连接、缓存等。
        此方法会在 run 方法的 finally 块中自动调用。
        """
        # 如果 CommandExecutor 需要释放资源，可以在这里添加
        # 注意：由于每次执行都创建新的 CommandExecutor，资源释放应该在
        # CommandExecutor 的 __del__ 或显式调用中完成
        pass