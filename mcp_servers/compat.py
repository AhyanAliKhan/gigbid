"""
MCP Server Compatibility Layer
Supports official MCP Python SDK v2.x (MCPServer), v1.x (FastMCP), and graceful fallback.
"""

try:
    from mcp.server.mcpserver import MCPServer
except (ImportError, ModuleNotFoundError):
    try:
        from mcp.server.fastmcp import FastMCP as MCPServer
    except (ImportError, ModuleNotFoundError):
        class MCPServer:
            def __init__(self, name: str = "mcp-server", *args, **kwargs):
                self.name = name

            def tool(self, name: str = None, description: str = None, *args, **kwargs):
                def decorator(fn):
                    return fn
                return decorator

            def resource(self, uri_template: str = None, *args, **kwargs):
                def decorator(fn):
                    return fn
                return decorator

            def prompt(self, name: str = None, *args, **kwargs):
                def decorator(fn):
                    return fn
                return decorator

            def run(self, *args, **kwargs):
                print(f"[{self.name}] Running mock MCP server")
