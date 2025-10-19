import csv
from collections import defaultdict
import html

"""
while(){}
if(){}
for(){}
else if(){}
else{}
do{} while();
switch(){}
case x:
default:
break;
continue;
"""

"""
types
conditional check - if, else if
loop check - for, while
switch branch - switch
case block
default block
do loop start - do
else branch - else
sequential - normal
"""

"""
final decision for switches
dictionary
switch id:[case 1, case 2, ..., default]
will get this from the scope when case or default is identified
this info is good, will deal with it later
"""

"""
corrections needed:
mark edge type, change next_ids to out_edges = {'sequential':[],'true':[], 'false':[], 'back':[], 'break':[]}
figure out where blocks are being created and closed and how they're being linked
"""
class BasicBlockNode:
    def __init__(self, node_id, typ, statements=None):
        self.id = node_id
        self.statements = statements if statements is not None else [] 
        self.out_edges = {"sequential":[], "true":[], "false":[], "back":[], "break":[]} # outgoing edges
        self.block_type = typ
    
    def set_type(self, typ):
        self.block_type = typ

    def add_statement(self, statement):
        self.statements.append(statement)

    def add_edge(self, target_id, edge_type): # add outgoing edge
        if target_id not in self.out_edges[edge_type]:
            self.out_edges[edge_type].append(target_id)

def construct_cfg(lines):
    # print("started constructing cfg\n")
    i=0
    kws = ("while(", "while ", "if(", "if ", "else if", "else", "for ", "for(", "do", "default:", "default ", "case ", "switch ", "switch(", "break ", "break;", "continue ", "continue;") # need to be cautious for else and do
    matched_kw = False
    n=len(lines)
    entry_block = BasicBlockNode(0,"sequential", ["Entry"])
    curr_block = BasicBlockNode(1,"sequential")
    next_id = 2
    nodes = {0:entry_block, 1:curr_block} # id:node
    scope = [] # scope stack, curr scope at end, pop when }, ids
    ifs = [] # stack to pair else and else if with nearest if and else if, id:"kw", kws are "if", "else", "elif"
    switches = {} # case or default id to switch id
    breaks = {} # break block id : id of block end it's looking for, deal with at the end
    entry_block.add_edge(1, "sequential")
    scope_end_next = {} # id, after block first, to resolve breaks at the end
    rets = []

    while i<n:
        matched_kw=False
        j=i
        # print(i)
        line = lines[i]
        # print(line)
        if line.startswith(kws):
            matched_kw = True
            if line.startswith("else") and len(line)>4 and line[4].isalnum(): # was a word starting with else, not else
                matched_kw=False
            if line.startswith("do") and len(line)>2 and line[2].isalnum(): # was a word starting with do like double
                matched_kw = False

        if matched_kw: # need to end prev block
            # print("hi")
            control_node = BasicBlockNode(next_id, "sequential", [line])
            if not line.startswith(("case", "default")):
                curr_block.add_edge(control_node.id, "sequential")
            curr_block=control_node
            nodes[next_id]=curr_block
            next_id+=1

            if line.startswith(("for", "while", "switch")):
                if line.startswith(("for", "while")):
                    curr_block.set_type("loop check")
                if line.startswith(("switch")):
                    curr_block.set_type("switch start")
                    switches[curr_block.id]=[]
                i+=2 # move on from this line and {
                scope.append(curr_block.id) # need to add these to scope 
                # print(curr_block.statements[0])
                content_block = BasicBlockNode(next_id, "sequential") # created a new block for content
                nodes[next_id]=content_block
                next_id+=1
                curr_block.add_edge(content_block.id, "true")
                curr_block = content_block
            
            elif line.startswith("break"):
                for sco in reversed(scope):
                    if nodes[sco].block_type=="loop check" or nodes[sco].block_type=="switch start":
                        breaks[curr_block.id]=sco # add an edge from this block to the first block outside this scope
                        break
                i+=1
                curr_block = BasicBlockNode(next_id, "sequential") # created a new block for content
                nodes[next_id]=curr_block
                next_id+=1
            
            elif line.startswith("continue"):
                for sco in reversed(scope):
                    if nodes[sco].block_type=="loop check":
                        curr_block.add_edge(sco, "back") # add an edge from this block to the loop check statement
                        break
                i+=1
                curr_block = BasicBlockNode(next_id, "sequential") # created a new block for content
                nodes[next_id]=curr_block
                next_id+=1

            elif line.startswith(("if", "else if")):
                curr_block.set_type("conditional check")
                i+=2 # skipping this line and next {
                scope.append(curr_block.id)
                # if line.startswith("else"): curr_block.out_edges["sequential"].pop() # remove sequential edge added above
                content_block = BasicBlockNode(next_id, "sequential") # created a new block for content
                nodes[content_block.id]=content_block
                next_id+=1
                curr_block.add_edge(content_block.id, "true")
                curr_block = content_block
            
            elif line.startswith("else"):
                curr_block.set_type("else branch")
                scope.append(curr_block.id)
                i+=2
                content_block = BasicBlockNode(next_id, "sequential") # created a new block for content
                nodes[content_block.id]=content_block
                next_id+=1
                curr_block.add_edge(content_block.id, "sequential")
                curr_block = content_block

            elif line.startswith(("case", "default")):
                curr_block.set_type("case_block" if line.startswith("case") else "default_block")
                # print(nodes[scope[-1]].statements[0])
                for sco in reversed(scope):
                    if nodes[sco].block_type=="switch start":
                        switches[sco].append(curr_block.id)
                        break
                scope.append(curr_block.id)
                i+=2
        
        elif line.startswith(("return ", "return;", "return(")):
            ret_block = BasicBlockNode(next_id, "sequential", [line])
            nodes[next_id] = ret_block
            curr_block.add_edge(next_id, "sequential")
            rets.append(next_id)
            next_id+=1
            new_block = BasicBlockNode(next_id, "sequential", [])
            nodes[next_id]=new_block
            curr_block=new_block
            next_id+=1
            i+=1

        else:
            if line=="}":
                if not len(scope)==0:
                    idx = scope.pop()
                    # print(scope)
                    if nodes[idx].block_type=="loop check": # for, while
                        curr_block.add_edge(idx, "back")
                        scope_end_next[idx]=next_id # store end so break knows where to go
                    elif nodes[idx].block_type=="do loop start": # do while
                        if lines[i+1].startswith("while ") or lines[i+1].startswith("while("):
                            while_block = BasicBlockNode(next_id, "loop check", [lines[i+1]]) # added the while condition
                            nodes[next_id]=while_block
                            i+=1
                            while_block.add_edge(idx, "true") # added back edge to do start
                            curr_block = while_block
                            next_id+=1
                            scope_end_next[idx]=next_id
                    elif nodes[idx].block_type=="switch start":
                        scope_end_next[idx]=next_id # store end so break knows where to go
                    elif nodes[idx].block_type=="conditional check": # don't know what to do: if, else if
                        nodes[idx].add_edge(next_id, "false")
                    # elif nodes[idx].block_type=="else branch": # ig need to store what it points to, body of if and else if need to point to that too
                    #     for pair in ifs[::-1]:
                    #         pair[0].add_edge(next_id, "sequential")
                    #         if pair[1]=="if": break

                    new_block = BasicBlockNode(next_id, "sequential") # intialising new block, does not have any statements yet
                    nodes[next_id]=new_block
                    curr_block.add_edge(next_id, "sequential")
                    curr_block = new_block
                    next_id+=1
                    i+=1
                else:
                    curr_block.add_statement(line)
                    i += 1
                
            else:
                curr_block.add_statement(line)
                i+=1
        if(j==i):
            # print(f"erroneous line{lines[j]}oiun")
            return nodes
    
    exit_block = BasicBlockNode(next_id, "sequential", ["Exit"])
    curr_block.add_edge(exit_block.id, "sequential")
    nodes[exit_block.id] = exit_block
    # resolving breaks
    for brk, sco in breaks.items():
        nodes[brk].add_edge(scope_end_next[sco], "break")
    # resolving switches
    for swi, cases in switches.items():
        for cas in cases:
            nodes[swi].add_edge(cas, "sequential")
    # resolving returns
    for ret in rets:
        nodes[ret].add_edge(exit_block.id, "sequential")
    # maybe remove a block if it just has one outgoing edge, which is sequential, and it doesn't have any statements
    # will need to add incoming edges to this to the block that I'll merge it with

    return nodes

import html

def gen_dot(nodes, filename):  # also calculates num nodes, num edges and cyclomatic complexity
    num_nodes = len(nodes)
    num_edges = 0

    dot_content = "digraph CFG {\n"

    for node_id, node in nodes.items():
        statement_text = "\n".join(node.statements)
        label = f"{node_id}\n{statement_text}"

        label = label.replace("\\", "\\\\")
        label = label.replace('"', "'")
        label = html.escape(label)

        dot_label = label.replace('\n', '\\n')

        if node_id == 0:
            dot_content += f' {node_id} [label="{dot_label}", shape=Mdiamond, style=filled, fillcolor="#ccffcc"];\n'
        elif any(s == "Exit" for s in node.statements):
            dot_content += f' {node_id} [label="{dot_label}", shape=Mdiamond, style=filled, fillcolor="#ffcccc"];\n'
        else:
            dot_content += f' {node_id} [label="{dot_label}"];\n'

    for source_id, node in nodes.items():
        for edge_type, targets in node.out_edges.items():
            for target_id in targets:
                if target_id not in nodes:
                    continue
                style = 'solid'
                color = 'black'
                label = ''
                if edge_type == 'true':
                    color = 'green'
                    label = 'T'
                    style = 'bold'
                elif edge_type == 'false':
                    color = 'red'
                    label = 'F'
                    style = 'dashed'
                elif edge_type == 'back':
                    color = 'blue'
                    label = 'Back'
                    style = 'dotted'
                elif edge_type == 'break':
                    color = 'purple'
                    label = 'Break'
                    style = 'dashed'

                dot_content += f' {source_id} -> {target_id} [label="{label}", color="{color}", style="{style}"];\n'
                num_edges += 1

    dot_content += "}\n"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(dot_content)

    cc = num_edges - num_nodes + 2
    return num_nodes, num_edges, cc

def export_cfg_nodes_to_csv(nodes, filename="cfg_nodes.csv"):
    # csv columns
    fieldnames = [
        'ID',
        'type',
        'statement_count',
        'statements',
        'sequential_edges',
        'true_edges',
        'false_edges',
        'back_edges',
        'break_edges'
    ]

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for node_id, node in nodes.items():
                # all statements in a single, |-separated string
                statements_str = ' | '.join(node.statements)
                # row data
                
                row = {
                    'ID': node_id,
                    'type': node.block_type,
                    'statement_count': len(node.statements),
                    'statements': statements_str,
                    'sequential_edges': ' | '.join(map(str, node.out_edges['sequential'])),
                    'true_edges': ' | '.join(map(str, node.out_edges['true'])),
                    'false_edges': ' | '.join(map(str, node.out_edges['false'])),
                    'back_edges': ' | '.join(map(str, node.out_edges['back'])),
                    'break_edges': ' | '.join(map(str, node.out_edges['break']))
                }
                writer.writerow(row)
        return True

    except Exception as e:
        print(f"An error occurred while writing the CSV: {e}")
        return False

def create_cfg(lines, filename):
    print("started the creating cfg process")
    nodes = construct_cfg(lines)
    print("control flow graph constructed\n")
    base = filename.rstrip(".c")
    dotfile = base+".dot"
    nodecsv = base+".csv"
    num_nodes, num_edges, cc = gen_dot(nodes, dotfile)
    print(f"complete control flow graph stored in {dotfile}\n")
    print(f"number of nodes = {num_nodes}")
    print(f"number of edges = {num_edges}")
    print(f"cyclomatic complexity = {cc}\n")
    done = export_cfg_nodes_to_csv(nodes, nodecsv)
    if(done): print(f"node and edge data stored in {nodecsv}\n")
    return num_nodes, num_edges, cc, dotfile, nodecsv, nodes
