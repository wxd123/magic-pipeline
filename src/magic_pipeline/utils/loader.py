from pathlib import Path
import sys
from typing import Any, Dict, Optional


class ConfigLoader:
    """配置加载器"""
    
    @staticmethod
    def find_files(config_dir: Path):
        """自动查找配置文件"""
        if not config_dir.exists():
            return None, None
        
        pipeline = next((config_dir / p for p in 
                        ["pipeline.yaml", "pipeline.yml", "config.yaml", "config.yml"] 
                        if (config_dir / p).exists()), None)
        prompt = next((config_dir / p for p in 
                      ["prompt.txt", "prompt.md", "template.txt", "template.md"] 
                      if (config_dir / p).exists()), None)
        return pipeline, prompt
    
    @staticmethod
    def load_yaml(path: Path) -> Optional[Dict[str, Any]]:
        try:
            import yaml
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️  读取配置失败: {e}")
            return None


def get_config_files(args):
    """获取配置路径"""
    if args.pipeline:
        return Path(args.pipeline), None
    elif args.config_path:
        pipeline, prompt = ConfigLoader.find_files(Path(args.config_path))
        if pipeline:
            print(f"🔍 自动发现配置文件: {pipeline}")
        if prompt:
            print(f"🔍 自动发现配置文件: {prompt}")
            
        return pipeline
    return None, None


def load_and_validate_config(args):
    """加载并验证配置，返回 (config, source_path)"""
    # 自动发现配置
    if args.config_path:
        pipeline, prompt = get_config_files(Path(args.config_path))
        if not pipeline:
            print(f"❌ 未找到 pipeline 配置文件")
            sys.exit(1)
        args.pipeline = str(pipeline)
        if prompt and not args.prompt_config:
            args.prompt_config = str(prompt)
            print(f"🔍 自动发现: {pipeline}\n   Prompt: {prompt}")
    
    if not args.pipeline and not args.clean:
        print("❌ 需要指定 --pipeline 或 --config-path")
        sys.exit(1)
    
    if not args.pipeline:
        return None, None  # clean 模式可能不需要配置    
    
    
    pipeline_config = ConfigLoader.load_yaml(pipeline)
    if not pipeline_config:
        sys.exit(1)
    
    prompt_config = ConfigLoader.load_yaml(prompt)
    if not prompt_config:
        sys.exit(1)
    
    return pipeline_config, prompt_config

