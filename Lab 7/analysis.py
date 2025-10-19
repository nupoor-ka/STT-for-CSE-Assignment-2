# analysis.py
import re
import csv
from collections import defaultdict

def extract_definition_lhs(stmt):
    if not stmt:
        return None
    s = stmt.strip()
    skip_prefixes = ("if ", "for ", "while ", "switch ", "case ", "return", "printf", "//", "/*", "*")
    if s.startswith(skip_prefixes):
        return None
    m = re.search(r'(?<![=!<>])=(?!=)', s)
    if not m:
        return None
    lhs = s[:m.start()].strip()
    lhs = re.sub(r'^\s*(?:unsigned|signed)?\s*(?:int|double|float|char|long|short|struct\s+\w+|void)\b', '', lhs).strip()
    if ',' in lhs:
        parts = lhs.split(',')
        lhs = parts[-1].strip()
    lhs = lhs.strip(" ()")
    tokens = re.split(r'\s+', lhs)
    lhs_var = tokens[-1] if tokens else lhs
    lhs_var = re.sub(r'\s+', '', lhs_var)
    if re.match(r'^[A-Za-z_]\w*(?:[\.\[].*)?$', lhs_var):
        return lhs_var
    return None

def build_predecessors(nodes):
    preds = {nid: set() for nid in nodes}
    for src_id, node in nodes.items():
        for targets in node.out_edges.values():
            for t in targets:
                if t in nodes:
                    preds[t].add(src_id)
    return preds

def compute_gen_kill(nodes, defs_map, var_to_defs):
    gen = {nid: set() for nid in nodes}
    for def_id, info in defs_map.items():
        gen[info['node']].add(def_id)
    kill = {nid: set() for nid in nodes}
    for nid in nodes:
        vars_defined = set(defs_map[d]['var'] for d in gen[nid])
        for v in vars_defined:
            kill[nid].update(var_to_defs[v] - gen[nid])
    return gen, kill

def collect_definitions(nodes):
    defs = []
    var_to_defs = defaultdict(set)
    for nid in sorted(nodes):
        node = nodes[nid]
        for stmt in node.statements:
            var = extract_definition_lhs(stmt)
            if var:
                def_id = f"D{len(defs)+1}"
                defs.append((def_id, var, nid, stmt))
                var_to_defs[var].add(def_id)
    defs_map = {d[0]: {'var': d[1], 'node': d[2], 'stmt': d[3]} for d in defs}
    return defs_map, {k: set(v) for k, v in var_to_defs.items()}

def iterative_dataflow(nodes):
    defs_map, var_to_defs = collect_definitions(nodes)
    gen, kill = compute_gen_kill(nodes, defs_map, var_to_defs)
    preds = build_predecessors(nodes)
    IN = {nid: set() for nid in nodes}
    OUT = {nid: set() for nid in nodes}
    iterations = []
    changed = True
    iteration_count = 0
    while changed:
        iteration_count += 1
        changed = False
        snapshot = {}
        for nid in sorted(nodes):
            new_in = set()
            for p in preds[nid]:
                new_in |= OUT[p]
            new_out = gen[nid] | (new_in - kill[nid])
            if new_in != IN[nid] or new_out != OUT[nid]:
                changed = True
            IN[nid] = new_in
            OUT[nid] = new_out
            snapshot[nid] = {
                'gen': set(gen[nid]),
                'kill': set(kill[nid]),
                'in': set(IN[nid]),
                'out': set(OUT[nid])
            }
        iterations.append(snapshot)
        if iteration_count > 5000:
            break
    return {
        'defs_map': defs_map,
        'var_to_defs': var_to_defs,
        'gen': gen,
        'kill': kill,
        'IN': IN,
        'OUT': OUT,
        'iterations': iterations
    }

def export_iterations_to_csv(results, filename):
    iterations = results['iterations']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Iteration", "BlockID", "gen[B]", "kill[B]", "in[B]", "out[B]"])
        for it, snap in enumerate(iterations, start=1):
            for nid in sorted(snap):
                row = snap[nid]
                fmt = lambda s: "{" + ", ".join(sorted(s)) + "}" if s else "{}"
                writer.writerow([
                    it,
                    nid,
                    fmt(row['gen']),
                    fmt(row['kill']),
                    fmt(row['in']),
                    fmt(row['out'])
                ])
    return filename

def export_definitions_map(results, filename):
    defs_map = results['defs_map']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["DefID", "Variable", "Node", "Statement"])
        for did in sorted(defs_map.keys(), key=lambda x: int(x[1:])):
            info = defs_map[did]
            writer.writerow([did, info['var'], info['node'], info['stmt']])
    return filename

def perform_reaching_definition_analysis(nodes, c_filename):
    base = c_filename.rstrip(".c")
    iter_file = base + "_reaching_definitions.csv"
    defs_file = base + "_definition_mapping.csv"
    results = iterative_dataflow(nodes)
    export_iterations_to_csv(results, iter_file)
    export_definitions_map(results, defs_file)
    print("reaching definition analysis completed")
    print(f"iterations table written to {iter_file}")
    print(f"definition mapping written to {defs_file}")
    return results
