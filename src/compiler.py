from pathlib import Path
from file_walker import TargetFile
from ast_parser import collapse_code

# The language map provided in your specification
LANG_MAP = {
    '.go': 'go',
    '.py': 'python',
    '.jl': 'julia',
    '.cs': 'csharp',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.c': 'c',
    '.h': 'c',
    '.cpp': 'cpp',
    '.hpp': 'cpp',
    '.java': 'java',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.md': 'markdown',
    '.json': 'json',
    '.xml': 'xml',
    '.yml': 'yaml',
    '.yaml': 'yaml',
    '.toml': 'toml',
    '.sh': 'bash',
    '.csproj': 'xml',
    'Dockerfile': 'dockerfile'
}

def generate_ascii_tree(target_files: list[TargetFile]) -> str:
    """Generates an ASCII file tree from the list of target paths."""
    if not target_files:
        return ""
        
    paths = [t.path for t in target_files]
    
    # Find the common root path so our tree isn't nested 10 layers deep starting from C:/
    all_parts = [p.parts for p in paths]
    min_len = min(len(p) for p in all_parts)
    common_len = 0
    for i in range(min_len):
        if len(set(p[i] for p in all_parts)) == 1:
            common_len += 1
        else:
            break
            
    root_path = Path(*all_parts[0][:common_len])
    
    # Build a nested dictionary representing the directory structure
    tree_dict = {}
    for path in paths:
        rel_parts = path.relative_to(root_path).parts
        current = tree_dict
        for part in rel_parts:
            current = current.setdefault(part, {})
            
    # Recursively format the dictionary into an ASCII tree
    lines = [f"📁 `{root_path.as_posix()}`"]
    def add_nodes(node_dict, prefix=""):
        keys = sorted(node_dict.keys())
        for i, key in enumerate(keys):
            is_last = (i == len(keys) - 1)
            connector = "└── " if is_last else "├── "
            child_prefix = "    " if is_last else "│   "
            
            if not node_dict[key]: # It's a file
                lines.append(f"{prefix}{connector}📄 `{key}`")
            else: # It's a directory
                lines.append(f"{prefix}{connector}📁 `{key}`")
                add_nodes(node_dict[key], prefix + child_prefix)
                
    add_nodes(tree_dict)
    return "\n".join(lines)

def compile_project_snapshot(target_files: list[TargetFile]) -> tuple[str, str]:
    """
    Returns a tuple containing: (ascii_tree_string, compiled_markdown_blocks_string)
    """
    # Generate the tree first
    tree_string = generate_ascii_tree(target_files)
    
    markdown_blocks = []
    for target in target_files:
        # ... [Keep the exact same logic you already have inside this loop] ...
        # (Reading text, finding decorator, collapse_code, format posix path)
        file_path = target.path
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            content = f"// Error reading file: {e}"

        ext = file_path.suffix.lower()
        name = file_path.name
        decorator = LANG_MAP.get(name, LANG_MAP.get(ext, 'text'))

        if target.collapse_functions and ext in ['.py', '.go', '.jl']:
            try:
                content = collapse_code(content, ext)
            except Exception as e:
                content += f"\n// Warning: Could not collapse functions: {e}"
        
        formatted_path = file_path.as_posix()
        block = f"## `{formatted_path}`\n\n```{decorator}\n{content}\n```\n"
        markdown_blocks.append(block)
        
    return tree_string, "\n".join(markdown_blocks)
