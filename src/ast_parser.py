from tree_sitter import Language, Parser, Node
import tree_sitter_python as tspython
import tree_sitter_go as tsgo
import tree_sitter_julia as tsjulia

# --- Initialize Languages ---
LANGUAGES = {
    '.py': Language(tspython.language()),
    '.go': Language(tsgo.language()),
    '.jl': Language(tsjulia.language()),
}

COMMENTS = {
    '.py': '\n    # Function body removed\n',
    '.go': '{\n\t// Function body removed\n}',
    '.jl': '\n    # Function body removed\nend',
}

def get_function_body_ranges(node: Node, ext: str) -> list[tuple[int, int]]:
    """
    Recursively walks the AST to find function bodies and returns their byte ranges.
    Preserves Python docstrings if present.
    """
    ranges = []
    
    # 1. Python Logic
    if ext == '.py':
        if node.type == 'function_definition':
            body_node = node.child_by_field_name('body') # This is usually a 'block' node
            if body_node:
                start_byte = body_node.start_byte
                
                # Check for a docstring: The first child of the block is an expression_statement
                # containing a string.
                if len(body_node.children) > 0:
                    first_stmt = body_node.children[0]
                    if first_stmt.type == 'expression_statement' and len(first_stmt.children) > 0:
                        if first_stmt.children[0].type == 'string':
                            # It's a docstring! Move the start byte to AFTER the docstring
                            start_byte = first_stmt.end_byte
                            
                ranges.append((start_byte, body_node.end_byte))
                
    # 2. Go Logic
    elif ext == '.go':
        if node.type in ('function_declaration', 'method_declaration'):
            body_node = node.child_by_field_name('body')
            if body_node:
                ranges.append((body_node.start_byte, body_node.end_byte))
                
    # 3. Julia Logic
    elif ext == '.jl':
        if node.type == 'function_definition':
            for child in reversed(node.children):
                if child.type != 'end' and child.type != 'identifier':
                    sig_end = node.children[1].end_byte 
                    ranges.append((sig_end, node.end_byte))
                    break

    # Recursively check all children
    for child in node.children:
        ranges.extend(get_function_body_ranges(child, ext))
        
    return ranges

def collapse_code(source_code: str, ext: str) -> str:
    """
    Parses the source code, finds function bodies, and replaces them with a comment.
    """
    if ext not in LANGUAGES:
        return source_code # Return unaltered if language isn't supported for collapsing

    parser = Parser(LANGUAGES[ext])
    
    # Tree-sitter requires bytes, not strings
    source_bytes = source_code.encode('utf-8')
    tree = parser.parse(source_bytes)
    
    # Get all body ranges
    body_ranges = get_function_body_ranges(tree.root_node, ext)
    
    # Sort ranges in reverse order (bottom of file to top)
    # This is CRITICAL: if we replace text from top to bottom, the byte 
    # offsets for everything below the first replacement will shift and break!
    body_ranges.sort(key=lambda x: x[0], reverse=True)
    
    comment_bytes = COMMENTS[ext].encode('utf-8')
    
    # Perform the replacements
    for start_byte, end_byte in body_ranges:
        source_bytes = source_bytes[:start_byte] + comment_bytes + source_bytes[end_byte:]
        
    return source_bytes.decode('utf-8')

# --- Simple Test Block ---
if __name__ == "__main__":
    # Let's test it with a quick snippet of Go code!
    sample_go = """
package main

import "fmt"

func Hello() {
    fmt.Println("Hello")
    fmt.Println("World")
}
    """
    print("Original Go Code:")
    print(sample_go)
    print("\nCollapsed Go Code:")
    print(collapse_code(sample_go, '.go'))