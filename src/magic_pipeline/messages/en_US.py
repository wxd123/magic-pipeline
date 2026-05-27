# magic_pipeline/messages/en_US.py
from typing import Dict
from magic_base.i18n import MessageProvider

class EnglishPipelineMessages(MessageProvider):
    """English messages"""
    
    @property
    def messages(self) -> Dict[str, str]:
        return {
            # Directory related
            "project_root_not_exists": (
                "Project root directory does not exist: {path}\n"
                "  Please verify the path is correct\n"
                "  Or create the directory: mkdir -p {path}"
            ),
            
            # Architecture related
            "mixed_layout": (
                "Invalid project structure: mixing src-layout and flat-layout\n"
                "  Project path: {path}\n"
                "  Issue: Detected both 'src/' directory and root-level Python package\n"
                "  Fix: Choose one architecture style and remove the other\n"
                "    - Keep src-layout: rm -rf {path}/{package}\n"
                "    - Keep flat-layout: rm -rf {path}/src"
            ),
            
            "no_valid_layout": (
                "Invalid project structure: No valid Python project architecture detected\n"
                "  Project path: {path}\n"
                "  Requirement: Must use one of the following architectures\n"
                "    - src-layout: Source code in src/ directory\n"
                "    - flat-layout: Source code in root-level package (directory with __init__.py)\n"
                "  Fix: Restructure your project to comply with the above standards"
            ),
            
            # Package name related
            "invalid_package_name": (
                "Invalid package name: '{package}'\n"
                "  Project path: {path}\n"
                "  Issue: Package name does not follow Python naming conventions\n"
                "  Requirement: Package names must use lowercase letters, digits, and underscores, and cannot start with a digit\n"
                "  Fix: Rename directory '{package}' to a compliant name\n"
                "    mv {package} <new_package_name>"
            ),
            
            "package_name_mismatch": (
                "Invalid project structure: Flat-layout root package name must match project name\n"
                "  Project path: {path}\n"
                "  Project name: {project_name}\n"
                "  Current package: {package}\n"
                "  Issue: Flat-layout requires the root package name to match the project name\n"
                "  Fix options:\n"
                "    Option 1 - Rename package: mv {package} {project_name}\n"
                "    Option 2 - Switch to src-layout: mkdir src && mv {package} src/\n"
                "    Option 3 - Rename project directory: cd .. && mv {project_name} {package}"
            ),
        }