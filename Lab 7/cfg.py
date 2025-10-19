"""
parser has code to parse and split into lines
constructor creates the nodes and edges and also stores a .dot file
visualizer opens the .dot file and creates a .png file with the plotted graph
analysis does reaching definition analysis and stores info in a .csv file
"""
from parser import parse_c
from constructor import create_cfg, BasicBlockNode
from visualizer import plot_cfg
from analysis import perform_reaching_definition_analysis
import pandas as pd

info = {"file_name":[], "num_nodes":[], "num_edges":[], "cyclomatic_complexity":[]}
if __name__=="__main__":
    paths = ["Lab 7 trial/c code files/bank_account_management.c", "Lab 7 trial/c code files/maze_solver.c", "Lab 7 trial/c code files/sort_search.c"]
    for file_path in paths:
        with open(file_path, "r") as fh:
            codestr = fh.read()
        lines = parse_c(codestr)
        print("code parsed\n")
        num_nodes, num_edges, cc, dotfile, csvfile, nodes = create_cfg(lines, file_path)
        # for node in nodes:
        #     print(f"Node {node.id}: {node.stmts} → {node.nxt}")
        info["file_name"].append(file_path)
        info["num_nodes"].append(num_nodes)
        info["num_edges"].append(num_edges)
        info["cyclomatic_complexity"].append(cc)

        results = perform_reaching_definition_analysis(nodes, file_path)
        
        filename = file_path.rstrip(".c")
        plot_cfg(dotfile)
        print()
    df = pd.DataFrame(info)
    df.to_csv("Lab 7 trial/c code files/metrics.csv", index=False)
    print("number of nodes, number of edges and cyclomatic complexity of all files stored in combined file metrics.csv")
