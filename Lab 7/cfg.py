from cparser import parse_c
import pandas as pd
import html
from visualizer import plot_cfg

"""
need to construct and plot a cfg
get code file, get it in text
plug into parse_c from cparser to split into lines
for(){}
while(){}
if(){}
else{}
else if (){}
switch()
{
case x:
pass;
break;
case y:
pass;
break;
default:
pass;
}
do
{
}
while()
;
find leader lines
identify basic blocks
store info in .dot format
plug into the visualizer.py code
store number of nodes, edges, cyclomatic complexity
"""

class Node:
    def __init__(self, id, statements=None):
        self.id = id
        self.stmts = statements or []
        self.nxt = []  # successors

    def add_nxt(self, node):
        if node.id not in self.nxt:
            self.nxt.append(node.id)

def generate_cfg(file_path):
    with open(file_path, "r") as fh:
        codestr = fh.read()

    lines = [line.strip() for line in parse_c(codestr) if line.strip()]
    n = len(lines)
    if n == 0:
        return [], []

    nodes = []
    stack = [] # stack entries: {'node': Node, 'type': 'if'|'while'|'for'|'switch'|'do', 'breaks': [Node,...], 'had_else': bool, 'has_default': bool}
    node_id = 0
    curr_block_lines = []

    def new_node(stmts):
        nonlocal node_id
        node = Node(node_id, stmts)
        nodes.append(node)
        node_id += 1
        return node

    entry = new_node(["Entry"])  # entry node
    prev = entry
    i = 0

    while i < n:
        line = lines[i]

        leader_keywords = ("if(", "while(", "for(", "switch(", "do", "else", "else if(", "break", "return", "case ", "default ")
        if line.startswith(leader_keywords) and not line.startswith("double"):
            if curr_block_lines: # flush straight-line block
                node = new_node(curr_block_lines)
                prev.add_nxt(node)
                prev = node
                curr_block_lines = []

            if line.startswith(("if(", "while(", "for(", "switch(", "do")): # handle block starting kws
                node = new_node([line])
                prev.add_nxt(node)
                if line.startswith("switch("):
                    stack.append({'node': node, 'type': 'switch', 'breaks': [], 'had_else': False, 'has_default': False})
                elif line.startswith("while("):
                    stack.append({'node': node, 'type': 'while', 'breaks': [], 'had_else': False, 'has_default': False})
                elif line.startswith("for("):
                    stack.append({'node': node, 'type': 'for', 'breaks': [], 'had_else': False, 'has_default': False})
                elif line.startswith("do"):
                    stack.append({'node': node, 'type': 'do', 'breaks': [], 'had_else': False, 'has_default': False})
                else:
                    stack.append({'node': node, 'type': 'if', 'breaks': [], 'had_else': False, 'has_default': False})
                prev = node

            elif line.startswith(("else", "else if(")):
                node = new_node([line])
                prev.add_nxt(node)
                # connect to last unmatched if
                for s in reversed(stack):
                    if s['type'] == 'if' and not s['had_else']:
                        s['node'].add_nxt(node)
                        s['had_else'] = True
                        break
                stack.append({'node': node, 'type': 'if', 'breaks': [], 'had_else': False, 'has_default': False})
                prev = node

            elif line.startswith(("case ", "default ")): # create case node and connect from nearest switch
                node = new_node([line])
                for s in reversed(stack):
                    if s['type'] == 'switch':
                        s['node'].add_nxt(node)
                        if line.startswith("default "):
                            s['has_default'] = True
                        break
                prev.add_nxt(node)
                prev = node # merge case/default with body lines
                # don't push case/default nodes onto stack

            elif line.startswith("break"):
                node = new_node([line])
                prev.add_nxt(node)
                if stack:
                    stack[-1]['breaks'].append(node)
                prev = node

            elif line.startswith("return"):
                node = new_node([line])
                prev.add_nxt(node)
                prev = node

        elif line == "{":
            pass

        elif line == "}":
            if stack:
                scope = stack.pop()
                header = scope['node']
                body_last = prev
                if scope['type'] in ('while', 'for', 'do'):
                    if body_last.id != header.id:
                        body_last.add_nxt(header)
                join = new_node([])  # join node after block

                # only connect header→join when fall-through possible
                connect_header = True
                if scope['type'] == 'if' and scope.get('had_else'):
                    connect_header = False
                if scope['type'] == 'switch' and scope.get('has_default'):
                    connect_header = False
                if connect_header:
                    header.add_nxt(join)

                for bnode in scope['breaks']:
                    bnode.add_nxt(join)
                prev = join
            else:
                prev = nodes[-1]

        else:
            if prev is not None and prev.stmts and (prev.stmts[0].startswith("case ") or prev.stmts[0].startswith("default ")):
                prev.stmts.append(line)
            else:
                curr_block_lines.append(line)

        i += 1

    if curr_block_lines:
        node = new_node(curr_block_lines)
        prev.add_nxt(node)
        prev = node

    exit_node = new_node(["Exit"])
    prev.add_nxt(exit_node)

    while stack:
        scope = stack.pop()
        for bnode in scope['breaks']:
            bnode.add_nxt(exit_node)

    edges = []
    for node in nodes:
        for nxt_id in node.nxt:
            edges.append((node.id, nxt_id))

    return nodes, edges

# introduced joins for simplicity, do not want them in the graph
def collapse_empty_joins(nodes, edges):
    id2node = {node.id: node for node in nodes}
    succs = {node.id: list(node.nxt)[:] for node in nodes}
    preds = {node.id: [] for node in nodes}
    for u, v in edges:
        preds[v].append(u)
    entry_ids = {node.id for node in nodes if node.stmts == ["Entry"]}
    exit_ids  = {node.id for node in nodes if node.stmts == ["Exit"]}
    remove_candidates = [node.id for node in nodes if (not node.stmts and node.id not in entry_ids and node.id not in exit_ids)]

    for j in remove_candidates: # rewire preds to succs for each removable node
        if j not in id2node:
            continue
        j_preds = list(preds.get(j, []))
        j_succs = list(succs.get(j, []))
        for p in j_preds:
            for s in j_succs:
                if p == s: 
                    continue
                if s not in succs.get(p, []):
                    succs.setdefault(p, []).append(s)
                    preds.setdefault(s, []).append(p)
        for p in j_preds: # remove j from pred succ lists and succ pred lists
            if j in succs.get(p, []):
                succs[p] = [x for x in succs[p] if x != j]
        for s in j_succs:
            if j in preds.get(s, []):
                preds[s] = [x for x in preds[s] if x != j]
        succs.pop(j, None)
        preds.pop(j, None)
        id2node.pop(j, None)

    remaining_nodes = [id2node[k] for k in sorted(id2node.keys())] # build remaining node list and remap ids
    old2new = {}
    new_nodes = []
    new_id = 0
    for node in remaining_nodes:
        old2new[node.id] = new_id
        node.id = new_id
        new_nodes.append(node)
        new_id += 1

    new_edges = set() # build new edges using succs, only for remaining nodes
    for old_u, out_list in succs.items():
        if old_u not in old2new:
            continue
        u = old2new[old_u]
        for old_v in out_list:
            if old_v not in old2new:
                continue
            v = old2new[old_v]
            if u == v:
                continue
            new_edges.add((u, v))

    new_edges = sorted(new_edges)
    for node in new_nodes: # update node.nxt lists
        node.nxt = []
    for u, v in new_edges:
        new_nodes[u].nxt.append(v)

    return new_nodes, new_edges

def write_dot(nodes, edges, out_path="cfg.dot"):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("digraph CFG {\n")
        for node in nodes: # escape quotes and backslashes safely
            label = "\n".join(node.stmts)
            label = label.replace("\\", "\\\\").replace('"', "'").replace("\"", "\\\"")
            label = html.escape(label)  # ensures no special chars break syntax

            f.write(f'  {node.id} [label="{label}", shape=box];\n')
        for u, v in edges:
            f.write(f'  {u} -> {v};\n')
        f.write("}\n")
    print(f"\ncontrol flow graph nodes and edges written to {out_path}")


def compute_cyclomatic_complexity(nodes, edges):
    n_nodes = len(nodes)
    n_edges = len(edges)
    return n_edges - n_nodes + 2

if __name__ == "__main__":
    info = {"file_name":[], "num_nodes":[], "num_edges":[], "cyclomatic_complexity":[]}
    while True:
        print("Enter file path (blank to exit): ", end="")
        file_path = input().strip()
        if file_path == "":
            break

        nodes, edges = generate_cfg(file_path)
        nodes, edges = collapse_empty_joins(nodes, edges) # removing join blocks
        # for node in nodes:
        #     print(f"Node {node.id}: {node.stmts} → {node.nxt}")

        cc = compute_cyclomatic_complexity(nodes, edges)
        print(f"\nnumber of nodes: {len(nodes)}")
        print(f"\nnumber of edges: {len(edges)}")
        print(f"\ncyclomatic complexity: {cc}")
        filename = list(file_path.split("/"))[-1]
        info["file_name"].append(filename)
        info["num_nodes"].append(len(nodes))
        info["num_edges"].append(len(edges))
        info["cyclomatic_complexity"].append(cc)
        filename = filename.rstrip(".c")
        write_dot(nodes, edges, f"cfg_{filename}.dot")
        plot_cfg(f"cfg_{filename}.dot")
        print()
    df = pd.DataFrame(info)
    df.to_csv("metrics.csv", index=False)
