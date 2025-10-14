"""
for al kinds of blocks, you can have either {block} or statement;
int main()
for(;;)
if(condition)
while()
do{}while()
goto label;
label: statement;
break
contiue
return
switch(){
    case x: statement;
    default: statement;
}
comments // or /* */
"""

def parse_c(codestr):
    n = len(codestr)
    lines = []
    i = 0
    reached_main = False
    found_opening_brace = True

    def skip_spaces(i):
        while i < n and codestr[i] in " \n\t\r":
            i += 1
        return i

    while i < n:
        if not reached_main:  # won't process anything outside int main()
            if codestr[i:i+4] == "int ":
                i += 4
                i = skip_spaces(i)
                if codestr[i:i+4] == "main":
                    i += 4
                    i = skip_spaces(i)
                    if i < n and codestr[i] == '(':
                        i += 1
                        while i < n and codestr[i] != ')':
                            i += 1
                        i += 1  # skip ')'
                        i = skip_spaces(i)
                        lines.append("int main()")
                        if i < n and codestr[i] == '{':
                            lines.append("{")
                            i += 1
                            reached_main = True
                        else:
                            found_opening_brace = False
                            reached_main = True
                    else:
                        i += 1
                else:
                    i += 1
            else:
                i += 1
            continue

        i = skip_spaces(i)
        if i >= n:
            break

        # skipping comments
        if codestr[i:i+2] == "//":
            while i < n and codestr[i] != '\n':
                i += 1
            continue
        if codestr[i:i+2] == "/*":
            while i < n-1 and codestr[i:i+2] != "*/":
                i += 1
            i += 2
            continue

        # keywords including switch/case/default
        keywords = ["for", "if", "else", "while", "do", "switch", "case", "default"]
        matched_kw = None
        for kw in keywords:
            if codestr.startswith(kw, i) and (i + len(kw) == n or (not codestr[i + len(kw)].isalnum())):
                matched_kw = kw
                break

        if matched_kw:
            line = matched_kw
            i += len(matched_kw)
            i = skip_spaces(i)

            # handle control structures with parentheses
            if matched_kw in ["for", "if", "while", "switch"]:
                if i < n and codestr[i] == '(':
                    cnt = 1
                    line += "("
                    i += 1
                    while i < n and cnt > 0:
                        if codestr[i] == '(':
                            cnt += 1
                        elif codestr[i] == ')':
                            cnt -= 1
                        line += codestr[i]
                        i += 1
                line = line.strip()
                lines.append(line)
                i = skip_spaces(i)
                # check next token
                if i < n and codestr[i] == '{':
                    lines.append("{")
                    i += 1
                else:
                    # single statement
                    stmt = ""
                    while i < n and codestr[i] not in [';', '{', '}']:
                        stmt += codestr[i]
                        i += 1
                    if i < n and codestr[i] == ';':
                        stmt += ';'
                        i += 1
                    if stmt.strip():
                        lines.append(stmt.strip())

            elif matched_kw == "else":
                if codestr[i:i+2]=="if": # else if(){}
                    i+=2
                    i = skip_spaces(i)
                    numbr = 0
                    stmt = "else if("
                    if codestr[i]=="(":
                        numbr+=1
                        i+=1
                    while i<n and numbr!=0:
                        if codestr[i]=="(":
                            numbr+=1
                        elif codestr[i]==")":
                            numbr-=1
                        stmt+=codestr[i]
                        i+=1
                    lines.append(stmt.strip())
                else: # else {}
                    lines.append("else")
                    i = skip_spaces(i)
                    if i < n and codestr[i] == '{':
                        lines.append("{")
                        i += 1
                    else:
                        stmt = ""
                        while i < n and codestr[i] not in [';', '{', '}']:
                            stmt += codestr[i]
                            i += 1
                        if i < n and codestr[i] == ';':
                            stmt += ';'
                            i += 1
                        if stmt.strip():
                            lines.append(stmt.strip())

            elif matched_kw == "do": # do {} while();
                if(codestr[i]!="u"):
                    lines.append("do")
                    i = skip_spaces(i)
                    if i < n and codestr[i] == '{':
                        lines.append("{")
                        i += 1
                    else:
                        stmt = ""
                        while i < n and codestr[i] not in [';', '{', '}']:
                            stmt += codestr[i]
                            i += 1
                        if i < n and codestr[i] == ';':
                            stmt += ';'
                            i += 1
                        if stmt.strip():
                            lines.append(stmt.strip())
                else: i-=2

            elif matched_kw in ["case", "default"]:
                stmt = matched_kw+" "
                while i < n and codestr[i] != ':':
                    stmt += codestr[i]
                    i += 1
                if codestr[i]==":":
                    stmt+=":"
                    i+=1
                lines.append(stmt.strip())

            continue

        if codestr[i] == '{':
            lines.append("{")
            i += 1
            continue
        elif codestr[i] == '}':
            lines.append("}")
            i += 1
            continue

        stmt = ""
        while i < n and codestr[i] != ';' and codestr[i] not in '{}':
            stmt += codestr[i]
            i += 1
        if i < n and codestr[i] == ';':
            stmt += ';'
            i += 1
        if stmt.strip():
            lines.append(stmt.strip())

    return lines
