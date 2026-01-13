"""
Tool Manager - Automatic Tool Discovery and Loading
Place this in: core/tool_manager.py

This automatically discovers and loads all tools from the tools/ directory!
"""
import os
import importlib
import inspect
from pathlib import Path


class ToolManager:
    """
    Automatically discovers and manages tools
    Just drop a tool file in tools/ folder and it's automatically available!
    """
    
    def __init__(self):
        self.tools = {}
        self.tool_instances = {}
        self.discover_tools()
    
    def discover_tools(self):
        """
        Automatically discover all tools in the tools/ directory
        No manual registration needed!
        """
        # Get the tools directory
        base_dir = Path(__file__).parent.parent
        tools_dir = base_dir / "tools"
        
        if not tools_dir.exists():
            print("⚠️ Tools directory not found")
            return
        
        # Find all Python files in tools/ (except __init__ and base_tool)
        tool_files = [
            f.stem for f in tools_dir.glob("*.py")
            if f.stem not in ["__init__", "base_tool", "__pycache__"]
        ]
        
        print(f"🔍 Scanning for tools... Found {len(tool_files)} files")
        
        # Import and register each tool
        for tool_file in tool_files:
            try:
                # Import the module
                module = importlib.import_module(f"tools.{tool_file}")
                
                # Find all classes in the module that are tools
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Check if it's a tool (has TOOL_NAME attribute and not the base class)
                    if hasattr(obj, 'TOOL_NAME') and name != 'BaseTool':
                        tool_id = tool_file  # Use filename as tool ID
                        
                        self.tools[tool_id] = {
                            "name": obj.TOOL_NAME,
                            "description": obj.TOOL_DESCRIPTION,
                            "category": obj.TOOL_CATEGORY,
                            "icon": obj.TOOL_ICON,
                            "class": obj,
                            "module": tool_file
                        }
                        
                        print(f"✅ Loaded: {obj.TOOL_ICON} {obj.TOOL_NAME}")
                        break  # Only one tool per file
                        
            except Exception as e:
                print(f"❌ Failed to load {tool_file}: {e}")
    
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
    
    def create_tool_instance(self, tool_id, parent):
        """Create an instance of a tool"""
        if tool_id not in self.tools:
            return None
        
        tool_class = self.tools[tool_id]["class"]
        return tool_class(parent)
    
    def reload_tools(self):
        """Reload all tools (useful for development)"""
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