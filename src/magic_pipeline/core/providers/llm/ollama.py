"""
Ollama LLM 提供者实现

该模块提供与 Ollama 服务的交互功能，包括：
- 服务生命周期管理（启动、检查）
- 模型下载、加载、卸载
- 文本生成

主要功能：
1. 自动检测并启动 Ollama 服务
2. 按需下载缺失的模型（显示进度）
3. 模型内存管理（加载/卸载）
4. 生成文本响应

使用示例：
    provider = OllamaProvider()
    if provider.ensure_model("qwen2.5-coder:0.5b"):
        response = provider.generate("qwen2.5-coder:0.5b", "Hello, world!")
"""

from typing import Optional, List
import subprocess
import time
import sys
import requests
from .llm_provider import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama 提供者实现"""
    
    def __init__(self, api_base: str = "http://localhost:11434"):
        """
        初始化 Ollama 提供者
        
        Args:
            api_base: Ollama API 基础 URL，默认为 http://localhost:11434
        """
        self.api_base = api_base
        self._current_model: Optional[str] = None
        self._service_process: Optional[subprocess.Popen] = None
    
    def get_provider_name(self) -> str:
        """返回提供者名称"""
        return "ollama"
    
    def is_available(self) -> bool:
        """
        检查 Ollama 服务是否可用
        
        Returns:
            bool: 服务可用返回 True，否则返回 False
        """
        try:
            response = requests.get(f"{self.api_base}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _ensure_service(self) -> bool:
        """
        确保 Ollama 服务正在运行
        
        如果服务未运行，尝试启动它。启动过程会显示进度提示。
        
        Returns:
            bool: 服务就绪返回 True，否则返回 False
        """
        # 检查服务是否已运行
        if self.is_available():
            print("[Ollama] ✓ 服务已就绪", flush=True)
            return True
        
        # 服务未运行，尝试启动
        print("[Ollama] ⚠ 服务未运行，正在启动...", flush=True)
        
        try:
            # 启动 Ollama 服务进程
            self._service_process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 等待服务启动，最多等待 30 秒
            print("[Ollama] 等待服务启动", end='', flush=True)
            for i in range(30):
                time.sleep(1)
                print(".", end='', flush=True)
                if self.is_available():
                    print("\n[Ollama] ✓ 服务启动成功", flush=True)
                    return True
            
            print("\n[Ollama] ✗ 服务启动超时（30秒）", flush=True)
            return False
            
        except FileNotFoundError:
            print("\n[Ollama] ✗ 错误: 未找到 ollama 命令", flush=True)
            print("[Ollama] 请安装 Ollama: https://ollama.ai/", flush=True)
            return False
        except Exception as e:
            print(f"\n[Ollama] ✗ 启动失败: {e}", flush=True)
            return False
    
    def ensure_model(self, model_name: str) -> bool:
        """
        确保指定模型可用
        
        该方法会按顺序执行：
        1. 确保 Ollama 服务正在运行
        2. 检查模型是否已下载，如未下载则自动下载
        3. 将模型加载到内存中
        
        Args:
            model_name: 模型名称，如 "qwen2.5-coder:0.5b"
            
        Returns:
            bool: 模型就绪返回 True，否则返回 False
        """
        print(f"\n[Ollama] 检查模型: {model_name}", flush=True)
        
        # 确保服务可用
        if not self._ensure_service():
            print("[Ollama] ❌ 服务不可用，无法加载模型", flush=True)
            return False
        
        # 如果模型已加载，直接返回
        if self._current_model == model_name:
            print(f"[Ollama] ✓ 模型 {model_name} 已加载", flush=True)
            return True
        
        # 卸载当前模型（如果有）
        if self._current_model:
            print(f"[Ollama] 卸载当前模型: {self._current_model}", flush=True)
            self.unload_model(self._current_model)
        
        # 检查模型是否已下载，未下载则自动下载
        if not self._model_exists(model_name):
            print(f"[Ollama] ⚠ 模型 {model_name} 未下载", flush=True)
            if not self._pull_model(model_name):
                return False
        
        # 加载模型到内存
        print(f"[Ollama] 加载模型: {model_name}", flush=True)
        return self.load_model(model_name)
    
    def load_model(self, model_name: str) -> bool:
        """
        加载模型到内存
        
        通过发送一个空请求来预热模型，使模型驻留在内存中。
        
        Args:
            model_name: 模型名称
            
        Returns:
            bool: 加载成功返回 True，否则返回 False
        """
        try:
            response = requests.post(
                f"{self.api_base}/api/generate",
                json={
                    "model": model_name,
                    "prompt": " ",
                    "stream": False,
                    "options": {"num_predict": 1}
                },
                timeout=30
            )
            if response.status_code == 200:
                self._current_model = model_name
                print(f"[Ollama] ✓ 模型 {model_name} 加载完成", flush=True)
                return True
            print(f"[Ollama] ✗ 模型 {model_name} 加载失败: HTTP {response.status_code}", flush=True)
            return False
        except Exception as e:
            print(f"[Ollama] ✗ 模型加载异常: {e}", flush=True)
            return False
    
    def unload_model(self, model_name: str) -> bool:
        """
        从内存中卸载模型
        
        通过设置 keep_alive=0 让 Ollama 立即释放模型占用的内存。
        
        Args:
            model_name: 模型名称
            
        Returns:
            bool: 卸载成功返回 True，否则返回 False
        """
        try:
            response = requests.post(
                f"{self.api_base}/api/generate",
                json={
                    "model": model_name,
                    "prompt": " ",
                    "stream": False,
                    "options": {"num_predict": 1},
                    "keep_alive": 0
                },
                timeout=10
            )
            if response.status_code == 200:
                if self._current_model == model_name:
                    self._current_model = None
                return True
            return False
        except:
            return False
    
    def generate(self, model_name: str, prompt: str, **kwargs) -> str:
        """
        生成文本响应
        
        使用指定的模型生成对提示词的响应。
        
        Args:
            model_name: 模型名称
            prompt: 输入提示词
            **kwargs: 其他参数，支持：
                - temperature: 温度参数（0-1），默认 0.3
                - max_tokens: 最大生成 token 数，默认 500
                - timeout: 请求超时时间（秒），默认 60
                
        Returns:
            str: 生成的文本，失败时返回错误信息
        """
        # 确保模型可用
        if not self.ensure_model(model_name):
            return f"[Error: Model {model_name} not available]"
        
        url = f"{self.api_base}/api/generate"
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.3),
                "num_predict": kwargs.get("max_tokens", 500),
            }
        }
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                timeout=kwargs.get("timeout", 60)
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except Exception as e:
            return f"[Error: {str(e)}]"
    
    def get_current_model(self) -> Optional[str]:
        """获取当前已加载的模型名称"""
        return self._current_model
    
    def list_models(self) -> List[str]:
        """
        列出已下载到本地的模型
        
        Returns:
            List[str]: 模型名称列表
        """
        try:
            response = requests.get(f"{self.api_base}/api/tags")
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        except:
            return []
    
    def _model_exists(self, model_name: str) -> bool:
        """
        检查模型是否已下载
        
        Args:
            model_name: 模型名称
            
        Returns:
            bool: 模型已下载返回 True
        """
        return model_name in self.list_models()
    
    def _pull_model(self, model_name: str) -> bool:
        """
        下载模型（显示实时进度）
        
        使用 subprocess.Popen 实时显示 ollama pull 的输出，
        让用户能够看到下载进度。
        
        Args:
            model_name: 模型名称
            
        Returns:
            bool: 下载成功返回 True
        """
        print(f"\n[Ollama] 开始下载模型: {model_name}", flush=True)
        print("[Ollama] 这可能需要几分钟时间，请耐心等待...", flush=True)
        print("="*60, flush=True)
        
        try:
            # 使用 Popen 以实时获取输出
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1  # 行缓冲，确保实时输出
            )
            
            # 实时打印输出（显示下载进度）
            for line in process.stdout:
                # 去除末尾换行符，但保留进度条格式
                line = line.rstrip('\n')
                if line:
                    print(f"  {line}", flush=True)
            
            process.wait()
            
            if process.returncode == 0:
                print("="*60, flush=True)
                print(f"[Ollama] ✓ 模型 {model_name} 下载完成", flush=True)
                return True
            else:
                print(f"[Ollama] ✗ 模型 {model_name} 下载失败 (返回码: {process.returncode})", flush=True)
                return False
                
        except subprocess.TimeoutExpired:
            print(f"[Ollama] ✗ 模型 {model_name} 下载超时（300秒）", flush=True)
            return False
        except FileNotFoundError:
            print("[Ollama] ✗ 错误: 未找到 ollama 命令", flush=True)
            print("[Ollama] 请先安装 Ollama: curl -fsSL https://ollama.ai/install.sh | sh", flush=True)
            return False
        except Exception as e:
            print(f"[Ollama] ✗ 模型下载出错: {e}", flush=True)
            return False