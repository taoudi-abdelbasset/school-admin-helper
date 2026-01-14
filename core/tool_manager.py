"""
Tool Manager - PyQt6 Version
Place this in: core/tool_manager.py
"""
import os
import importlib
import inspect
from pathlib import Path


class ToolManager:
    """
    Automatically discovers and manages tools
    Now supports PyQt6!
    """
    
    def __init__(self):
        self.tools = {}
        self.tool_instances = {}
        self.discover_tools()
    
    def discover_tools(self):
        """
        Automatically discover all tools in the tools/ directory
        """
        base_dir = Path(__file__).parent.parent
        tools_dir = base_dir / "tools"
        
        if not tools_dir.exists():
            print("⚠️ Tools directory not found")
            return
        
        # Find all Python files in tools/
        tool_files = [
            f.stem for f in tools_dir.glob("*.py")
            if f.stem not in ["__init__", "base_tool", "base_tool_pyqt6", "__pycache__"]
        ]
        
        print(f"🔍 Scanning for tools... Found {len(tool_files)} files")
        
        # Import and register each tool
        for tool_file in tool_files:
            try:
                module = importlib.import_module(f"tools.{tool_file}")
                
                # Find all classes that are tools
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if hasattr(obj, 'TOOL_NAME') and name not in ['BaseTool', 'BaseToolPyQt6']:
                        tool_id = tool_file
                        
                        self.tools[tool_id] = {
                            "name": obj.TOOL_NAME,
                            "description": obj.TOOL_DESCRIPTION,
                            "category": obj.TOOL_CATEGORY,
                            "icon": obj.TOOL_ICON,
                            "class": obj,
                            "module": tool_file
                        }
                        
                        print(f"✅ Loaded: {obj.TOOL_ICON} {obj.TOOL_NAME}")
                        break
                        
            except Exception as e:
                print(f"❌ Failed to load {tool_file}: {e}")
                import traceback
                traceback.print_exc()
    
    def get_tool(self, tool_id):
        """Get tool info by ID"""
        return self.tools.get(tool_id)
    
    def get_all_tools(self):
        """Get all discovered tools"""
        return self.tools
    
    def get_tools_by_category(self, category):
        """Get tools filtered by category"""
        return {
            tid: info for tid, info in self.tools.items()
            if info["category"] == category
        }
    
    def get_categories(self):
        """Get all unique categories"""
        categories = set()
        for tool in self.tools.values():
            categories.add(tool["category"])
        return sorted(list(categories))
    
    def create_tool_instance_pyqt6(self, tool_id, parent=None):
        """Create PyQt6 instance of a tool"""
        if tool_id not in self.tools:
            return None
        
        tool_class = self.tools[tool_id]["class"]
        return tool_class(parent)
    
    def reload_tools(self):
        """Reload all tools"""
        self.tools.clear()
        self.tool_instances.clear()
        self.discover_tools()


# Singleton instance
_tool_manager = None

def get_tool_manager():
    """Get the global tool manager instance"""
    global _tool_manager
    if _tool_manager is None:
        _tool_manager = ToolManager()
    return _tool_manager