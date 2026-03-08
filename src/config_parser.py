import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# --- STEP 1: Data Structures ---

@dataclass
class FilesConfig:
    """Represents a [[Files]] block in the TOML configuration."""
    paths: list[str] = field(default_factory=list)
    collapse_functions: bool = False

@dataclass
class FoldersConfig:
    """Represents a [[Folders]] block in the TOML configuration."""
    paths: list[str] = field(default_factory=list)
    include: str = ""
    exclude: str = ""
    collapse_functions: bool = False

@dataclass
class ProjectConfig:
    """Holds the entire parsed configuration."""
    files: list[FilesConfig] = field(default_factory=list)
    folders: list[FoldersConfig] = field(default_factory=list)


# --- STEP 2: Configuration Parser ---

def parse_config(file_path: str | Path) -> ProjectConfig:
    """
    Reads a TOML configuration file and maps it to the ProjectConfig dataclass.
    """
    with open(file_path, "rb") as f:
        data = tomllib.load(f)
        
    project_config = ProjectConfig()
    
    # Extract [[Files]] blocks
    for file_data in data.get("Files", []):
        # Look for "Paths" first, fallback to "Path", default to []
        extracted_paths = file_data.get("Paths", file_data.get("Path", []))
        
        config = FilesConfig(
            paths=extracted_paths,
            collapse_functions=file_data.get("CollapseFunctions", False)
        )
        project_config.files.append(config)
        
    # Extract [[Folders]] blocks
    for folder_data in data.get("Folders", []):
        # Look for "Paths" first, fallback to "Path", default to []
        extracted_paths = folder_data.get("Paths", folder_data.get("Path", []))
        
        config = FoldersConfig(
            paths=extracted_paths,
            include=folder_data.get("Include", ""),
            exclude=folder_data.get("Exclude", ""),
            collapse_functions=folder_data.get("CollapseFunctions", False)
        )
        project_config.folders.append(config)
        
    return project_config

# --- Simple Test Block ---
if __name__ == "__main__":
    # You can test this by creating a "myproject.toml" with your example data
    # in the same directory and running this script.
    test_file = Path("myproject.toml")
    if test_file.exists():
        config = parse_config(test_file)
        print(f"Loaded {len(config.files)} File blocks and {len(config.folders)} Folder blocks.")
        print("First Folder's Include string:", config.folders[0].include)
    else:
        print(f"Create a {test_file} to test the parser!")