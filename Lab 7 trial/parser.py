import re

def parse_c(codestr: str) -> list:

    def remove_comments(text):
        text = re.sub(r'/\*[\s\S]*?\*/', '', text)
        text = re.sub(r'//.*', '', text)
        return text

    code_without_comments = remove_comments(codestr)

    main_header_str = 'int main() {'
    main_pattern = re.compile(
        r'(int\s+main\s*\(\s*(?:void|int\s+argc,\s*char\s*\*\s*argv\[\])?\s*\)\s*\{)([\s\S]*)\}', 
        re.DOTALL
    )
    match = main_pattern.search(code_without_comments)

    if not match:
        return []

    main_body = match.group(2).strip()
    temp_code = main_body
    temp_code = temp_code.replace('{', ' { ')
    temp_code = temp_code.replace('}', ' } ')
    temp_code = temp_code.replace(';', ' ; ')
    
    normalized_tokens = [token for token in temp_code.split() if token]
    
    final_list = [main_header_str[:-2].strip(), main_header_str[-1]] # 'int main()' and '{'
    current_statement = []
    
    header_kws = ('if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default')

    for i, token in enumerate(normalized_tokens):
        if token in ('{', '}'):
            if current_statement:
                final_list.append(" ".join(current_statement).strip())
                current_statement = []
            final_list.append(token)
            
        elif token == ';':
            if not current_statement and final_list and final_list[-1] in header_kws:
                current_statement.append(final_list.pop()) # Get back the header
                
            current_statement.append(token)
            statement = " ".join(current_statement).strip()
            final_list.append(statement)
            current_statement = []
            
        elif token == ':':
            current_statement.append(token)
            statement = " ".join(current_statement).strip()
            final_list.append(statement)
            current_statement = []
            
        else:
            current_statement.append(token)
            
    if current_statement:
        statement = " ".join(current_statement).strip()
        if statement:
            final_list.append(statement)

    output = []
    i = 0
    m = len(final_list)
    while i < m:
        item = final_list[i].strip()

        if item.startswith("for ") or item.startswith("for("):
            strr = final_list[i].strip()+final_list[i+1].strip()+final_list[i+2].strip()
            output.append(strr)
            i+=3

        elif item == 'else' and i + 1 < m and final_list[i+1].strip() == 'if':
            j = i + 2
            while j < m and final_list[j] not in ('{', '}'):
                j += 1
            
            condition_tokens = final_list[i:j]
            output.append(" ".join(condition_tokens).strip())
            i = j
            continue

        elif item.endswith(';}'):
            output.append(item[:-2] + ';')
            output.append('}')
            i += 1
            continue
            
        else:
            output.append(item)
            i += 1
            
    output = output[2:-1]
    return [s for s in output if s]