import os
from dataclasses import dataclass
from pathlib import Path
from config_parser import ProjectConfig

# --- Data Structure for Output ---

@dataclass
class TargetFile:
    """Represents a single file that needs to be processed."""
    path: Path
    collapse_functions: bool

# --- File Walking Logic ---

def get_files_to_process(config: ProjectConfig) -> list[TargetFile]:
    """
    Traverses the file system based on the config and returns a list of target files.
    """
    target_files: list[TargetFile] = []
    
    # 1. Process explicit [[Files]] blocks
    for file_block in config.files:
        for file_path_str in file_block.paths:
            # Resolve to absolute path as requested in the spec
            file_path = Path(file_path_str).resolve()
            if file_path.is_file():
                target_files.append(TargetFile(
                    path=file_path,
                    collapse_functions=file_block.collapse_functions
                ))

    # 2. Process [[Folders]] blocks
    for folder_block in config.folders:
        # Parse Include and Exclude rules
        # Split by comma. e.g., ".go," becomes [".go", ""]
        include_list = folder_block.include.split(",") if folder_block.include else []
        exclude_set = set(folder_block.exclude.split(",")) if folder_block.exclude else set()

        for folder_path_str in folder_block.paths:
            folder_path = Path(folder_path_str).resolve()
            
            if not folder_path.is_dir():
                continue

            # Walk the directory tree
            for root, dirs, files in os.walk(folder_path):
                # Modify 'dirs' in-place to prune excluded folders
                # os.walk will not visit directories removed from this list
                dirs[:] = [d for d in dirs if d not in exclude_set]
                
                for file_name in files:
                    file_path = Path(root) / file_name
                    file_suffix = file_path.suffix
                    
                    # Check inclusion logic
                    # A file is included if its suffix is in the list, 
                    # OR if it has no suffix and "" is in the list.
                    is_included = False
                    if not include_list: # If empty include list, include nothing
                        pass
                    elif file_suffix in include_list:
                        is_included = True
                    elif file_suffix == "" and "" in include_list:
                        is_included = True

                    if is_included:
                        target_files.append(TargetFile(
                            path=file_path,
                            collapse_functions=folder_block.collapse_functions
                        ))
                        
    # Remove duplicates in case configurations overlap, preserving order
    unique_targets = []
    seen_paths = set()
    for target in target_files:
        if target.path not in seen_paths:
            unique_targets.append(target)
            seen_paths.add(target.path)

    return unique_targets

# --- Simple Test Block ---
if __name__ == "__main__":
    from config_parser import parse_config
    
    test_file = Path("myproject.toml")
    if test_file.exists():
        config = parse_config(test_file)
        targets = get_files_to_process(config)
        print(f"Discovered {len(targets)} files to process.")
        if targets:
            print(f"First file: {targets[0].path} (Collapse: {targets[0].collapse_functions})")