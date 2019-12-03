import sys
from graphviz import Digraph

# See docs for reference - http://graphviz.readthedocs.io/en/stable/#

dot = None
OUTPUT = 'm2dfg'

def init_digraph():
    global dot
    if dot is None:
        dot = Digraph(OUTPUT, filename='%s.gv'%OUTPUT)

def statement(label, node_name=''):
    dot.node(label, node_name, shape='invtriangle')

def data(label, node_name=''):
    dot.node(label, node_name, shape='box')

def main():
    init_digraph()
    
    data('p_0', '<N<sup>3</sup> + 4N<sup>2</sup>>')
    statement('p_1', 'Fx1')
    
    data('u_0', '<N<sup>3</sup> + 4N<sup>2</sup>>')
    statement('u_1', 'Fx1')

    data('p_2', '<N<sup>3</sup> + N<sup>2</sup>>')
    data('u_2', '<N<sup>3</sup> + N<sup>2</sup>>')

    with dot.subgraph(name='cluster_0') as c:
        c.attr(style='filled')
        c.attr(color='white')
        c.node_attr.update(style='filled', color='white')
        c.edges([('p_0', 'p_1'), ('p_1', 'p_2'), ('p_0', 'p_2')])
        c.attr(label='&rho;')

    with dot.subgraph(name='cluster_1') as c:
        c.node_attr.update(style='filled')
        c.edges([('u_0', 'u_1'), ('u_1', 'u_2')])
        c.attr(label='<<i>u</i>>')
        c.attr(color='white')

    dot.edge('p_1', 'u_2')

    code = dot.source
    fp = open(sys.argv[1], 'w')
    fp.write(code)
    fp.close()

    dot.render(OUTPUT, view=True) # defaults to PDF output

main()