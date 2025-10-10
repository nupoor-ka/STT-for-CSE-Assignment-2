"""
need to construct and plot a cfg
get code file, get it in text
know how to parse it to split into lines, manage strings properly
store indices too
keep these originals, create tuples of these too
remove empty lines, comments
then get two tuples, lines and their indices
skip everything inside quotes
;, \n, ", ', //, /*
while, for, if, else, else if, match, case, do while
find leader lines
identify basic blocks
store info in .dot format
plug into the visualizer.py code
store number of nodes, edges, cyclomatic complexity
"""

while True:
    print("Enter file path, enter blank if done processing all files:")
    file_path = input()
    if file_path=="":
        break
    with open(file_path, "r") as fh:
        raw_string = fh.read()
    lines = []
    line_yet = ""
    for i in range(len(raw_string)): # splitting it into lines, ignoring blanks, ignoring comment only
        c = raw_string[i]
        if c=='f' and i+2<len(raw_string) and raw_string[i+1]=='o' and raw_string[i+2]=='r':
            line_yet+="for" # checking for 'for' because that has ; without it ending line
            s = []
            i+=3
            s.append(raw_string[i])
            i+=1
            while i<len(raw_string) and len(s)!=0:
                if raw_string[i]=='(':
                    s.append('(')
                elif raw_string[i]==')':
                    s.pop()
                line_yet+=raw_string[i]
                i+=1
        elif c==";" or (c=="\\" and raw_string[i+1]=="n"): # newline or ; breaks
            line_yet.strip()
            if line_yet!="" and line_yet[0:2]!="//" and line_yet[0:2]!="/*":
                lines.append(line_yet)
                line_yet=""
            i+=1
        elif c=='"': # processing string so \n inside string doesn't break code
            line_yet+=c
            i+=1
            while i<len(raw_string) and raw_string[i]!='"':
                line_yet+=raw_string[i]
                i+=1
        elif c=="'": # processing char
            line_yet+=c
            i+=1
            while i<len(raw_string) and raw_string[i]!="'":
                line_yet+=raw_string[i]
                i+=1
        elif c=="/": # processing comments
            if raw_string[i+1]=="/": # single-line
                while i<len(raw_string) and raw_string[i]!="\\": 
                    i+=1
                else:
                    if i==len(raw_string): break
                    else: i-=1 # because found a \
            elif raw_string[i+1]=="*": # multi-line
                while i<len(raw_string) and raw_string[i:i+2]!="*/":
                    i+=1
        i+=1
    # done splitting it into lines
    # now need to process lines separately
    # maybe can start by marking all of them -1, first leader line is 0, next is 1, so on
    # their corresponding basic blocks can have their number too
    # store indices of leader lines
    leaders = []
    line_blk_ids = []
    for i in range(len(lines)):
        line_blk_ids.append(-1)
    i=0
    while i<len(lines):
        if lines[i][0:10]=="int main()":
            i+=1
