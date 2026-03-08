from tree_sitter import Language, Parser, Node
import tree_sitter_python as tspython
import tree_sitter_go as tsgo
import tree_sitter_julia as tsjulia
import tree_sitter_javascript as tsjs
import tree_sitter_c_sharp as tscsharp

# --- Initialize Languages ---
LANGUAGES = {
    '.py': Language(tspython.language()),
    '.go': Language(tsgo.language()),
    '.jl': Language(tsjulia.language()),
    '.js': Language(tsjs.language()),
    '.cs': Language(tscsharp.language()),
}

COMMENTS = {
    '.py': '\n    # Function body removed\n',
    '.go': '{\n\t// Function body removed\n}',
    '.jl': '\n    # Function body removed\nend',
    '.js': '{\n\t// Function body removed\n}',
    '.cs': '{\n\t// Function body removed\n}',
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
            body_node = node.child_by_field_name('body')
            if body_node:
                start_byte = body_node.start_byte
                if len(body_node.children) > 0:
                    first_stmt = body_node.children[0]
                    if first_stmt.type == 'expression_statement' and len(first_stmt.children) > 0:
                        if first_stmt.children[0].type == 'string':
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

    # 4. JavaScript Logic
    elif ext == '.js':
        # Catches standard functions, arrow functions, and class methods
        if node.type in ('function_declaration', 'arrow_function', 'method_definition'):
            body_node = node.child_by_field_name('body')
            if body_node and body_node.type == 'statement_block':
                ranges.append((body_node.start_byte, body_node.end_byte))

    # 5. C# Logic
    elif ext == '.cs':
        # Catches standard methods, constructors, and local functions
        if node.type in ('method_declaration', 'constructor_declaration', 'local_function_statement'):
            body_node = node.child_by_field_name('body')
            if body_node:
                ranges.append((body_node.start_byte, body_node.end_byte))

    # Recursively check all children (handles nested functions/methods)
    for child in node.children:
        ranges.extend(get_function_body_ranges(child, ext))
        
    return ranges

def collapse_code(source_code: str, ext: str) -> str:
    """
    Parses the source code, finds function bodies, and replaces them with a comment.
    """
    if ext not in LANGUAGES:
        return source_code

    parser = Parser(LANGUAGES[ext])
    source_bytes = source_code.encode('utf-8')
    tree = parser.parse(source_bytes)
    
    body_ranges = get_function_body_ranges(tree.root_node, ext)
    body_ranges.sort(key=lambda x: x[0], reverse=True)
    
    comment_bytes = COMMENTS[ext].encode('utf-8')
    for start_byte, end_byte in body_ranges:
        source_bytes = source_bytes[:start_byte] + comment_bytes + source_bytes[end_byte:]
        
    return source_bytes.decode('utf-8')