"""
code to draw a cfg
will have a .dot file
need to use Graphviz to plot the cfg and store it
"""

from graphviz import Source

def plot_cfg(source_file):
    src = Source.from_file(source_file)
    name = source_file.removesuffix(".dot")
    src.render(name, format='png', cleanup=True) # cleanup deletes source file, not needed anymore
    print(f"control flow graph stored as an image at {name}.png\n")
    