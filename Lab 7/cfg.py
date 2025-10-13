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
    stack = []  # keeps track of open control blocks
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

        # leader lines
        leader_keywords = ("if(", "while(", "for(", "switch(", "do", "else", "else if(", "break", "return", "case ", "default ")
        if line.startswith(leader_keywords):
            if curr_block_lines: # starting new block if current block has lines
                node = new_node(curr_block_lines)
                prev.add_nxt(node)
                prev = node
                curr_block_lines = []

            if line.startswith(("if(", "while(", "for(", "switch(", "do")):
                node = new_node([line]) #  new block for the leader
                prev.add_nxt(node)
                stack.append(node) # stack for nested structures
                prev = node
            elif line.startswith(("else", "else if(")): # else connects to the parent if
                node = new_node([line])
                prev.add_nxt(node)
                if stack and "if(" in stack[-1].stmts[0]:
                    parent = stack[-1]
                    parent.add_nxt(node)
                    stack.append(node)
                prev = node
            else: # for case, default
                curr_block_lines.append(line)

        elif line == "{": pass # ignore, just a block start
        elif line == "}": # close current block
            if stack:
                block = stack.pop() # back edge for loops
                if block.stmts[0].startswith(("while(", "for(")) or block.stmts[0] == "do":
                    prev.add_nxt(block)
            prev = nodes[-1]
        else: # normal statement, add to current block
            curr_block_lines.append(line)

        i += 1

    if curr_block_lines: # remaining statements
        node = new_node(curr_block_lines)
        prev.add_nxt(node)
        prev = node

    exit_node = new_node(["Exit"])
    prev.add_nxt(exit_node)

    edges = [] # build edges
    for node in nodes:
        for nxt_id in node.nxt:
            edges.append((node.id, nxt_id))

    return nodes, edges


def write_dot(nodes, edges, out_path="cfg.dot"):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("digraph CFG {\n")
        for node in nodes:
            # Escape quotes and backslashes safely
            label = "\n".join(node.stmts)
            label = label.replace("\\", "\\\\").replace('"', "'").replace("\"", "\\\"")
            label = html.escape(label)  # ensures no special chars break syntax

            f.write(f'  {node.id} [label="{label}", shape=box];\n')
        for u, v in edges:
            f.write(f'  {u} -> {v};\n')
        f.write("}\n")
    print(f"CFG written to {out_path}")


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
        for node in nodes:
            print(f"Node {node.id}: {node.stmts} → {node.nxt}")

        cc = compute_cyclomatic_complexity(nodes, edges)
        print(f"\nNumber of Nodes: {len(nodes)}")
        print(f"\nNumber of Edges: {len(edges)}")
        print(f"\nCyclomatic Complexity: {cc}")
        filename = list(file_path.split("/"))[-1]
        info["file_name"].append(filename)
        info["num_nodes"].append(len(nodes))
        info["num_edges"].append(len(edges))
        info["cyclomatic_complexity"].append(cc)
        filename = filename.rstrip(".c")
        write_dot(nodes, edges, f"cfg_{filename}.dot")
        plot_cfg(f"cfg_{filename}.dot")
    df = pd.DataFrame(info)
    df.to_csv("metrics.csv", index=False)
