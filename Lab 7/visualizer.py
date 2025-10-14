"""
code to draw a cfg
will have a .dot file
need to use Graphviz to plot the cfg and store it
"""

from graphviz import Source

def plot_cfg(source_file):
    src = Source.from_file(source_file)
    name = source_file.removesuffix(".dot")
    src.render(name, format='png', cleanup=True)  # creates cfg_output.png
    print(f"\ncontrol flow graph stored as an image at {name}.png")
