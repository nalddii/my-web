import os
import ast
import pkg_resources
from pathlib import Path

class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name.split('.')[0])

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module.split('.')[0])

def find_imports_in_file(file_path):
    """Extract import statements from a Python file."""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            tree = ast.parse(content)
            visitor = ImportVisitor()
            visitor.visit(tree)
            imports.update(visitor.imports)
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
    
    return imports

def get_installed_packages():
    """Get a dictionary of installed packages and their versions."""
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def is_standard_library(module_name):
    """Check if a module is part of Python's standard library."""
    import sys
    import importlib.util
    
    if module_name in sys.stdlib_module_names:  # Python 3.10+
        return True
    
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return False
    
    return 'site-packages' not in str(spec.origin)

def generate_requirements(project_path):
    """Generate requirements.txt from a project folder."""
    all_imports = set()
    python_files = []
    
    # Find all Python files in the project
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Process each Python file
    for file_path in python_files:
        file_imports = find_imports_in_file(file_path)
        all_imports.update(file_imports)
    
    # Get installed packages
    installed_packages = get_installed_packages()
    
    # Filter out standard library modules and match with installed packages
    requirements = []
    for imp in all_imports:
        if not is_standard_library(imp):
            # Handle common package name variations
            pkg_name = imp.lower().replace('-', '_')
            
            # Check if package is installed
            if pkg_name in installed_packages:
                requirements.append(f"{pkg_name}=={installed_packages[pkg_name]}")
            else:
                print(f"Warning: Package '{imp}' is imported but not installed")
    
    # Sort requirements alphabetically
    requirements.sort()
    
    # Write to requirements.txt
    output_path = os.path.join(project_path, 'requirements.txt')
    with open(output_path, 'w') as f:
        f.write('\n'.join(requirements))
    
    print(f"\nRequirements file generated at: {output_path}")
    print(f"Found {len(requirements)} packages:")
    for req in requirements:
        print(f"  - {req}")
    
    if len(requirements) == 0:
        print("\nNo third-party packages were detected. This might indicate that:")
        print("1. The project only uses standard library modules")
        print("2. The required packages are not installed in the current environment")
        print("3. The import statements are using different names than the installed packages")

def main():
    # Get project path from user input or use current directory
    project_path =r"C:\Users\62812\Documents\Self improvement\MyWeb"
    
    if not project_path:
        project_path = os.getcwd()
    
    # Verify if the path exists
    if not os.path.exists(project_path):
        print("Error: The specified path does not exist.")
        return
    
    print(f"\nAnalyzing project at: {project_path}")
    generate_requirements(project_path)

if __name__ == "__main__":
    main()