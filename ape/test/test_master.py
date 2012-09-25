from ape.util import unique, load_dict
from ape.master import sanitize, make_apply, distribute
from ape.theano_util import shape_of_variables
import theano
import os

def test_sanitize():
    x = theano.tensor.matrix('x')
    y = x.T
    z = y + 1
    sanitize((x,), (z,))
    assert all(v.name and '.' not in v.name for v in (x,y,z))
    assert unique((x,y,z))
    print x, y, z

def test_make_apply():
    x = theano.tensor.matrix('x')
    y = theano.tensor.matrix('y')
    op = theano.tensor.elemwise.Sum()
    job = ((x,), op, y)
    apply = make_apply(*job)
    assert isinstance(apply, theano.Apply)
    assert apply.op == op
    assert apply.inputs[0].name == x.name
    assert apply.outputs[0].name == y.name

def test_integration():
    from ape.examples.basic_computation import inputs, outputs, input_shapes
    from ape.examples.basic_computation import a,b,c,d,e
    from ape.examples.basic_network import machines, A, B
    from ape import timings
    comm_dict = load_dict("ape/test/integration_test_comm_dict.dat")
    comp_dict = load_dict("ape/test/integration_test_comp_dict.dat")

    rootdir = '_test/'
    os.system('mkdir -p %s'%rootdir)
    sanitize(inputs, outputs)

    known_shapes = shape_of_variables(inputs, outputs, input_shapes)
    comptime = timings.make_runtime_function(comp_dict)
    commtime = timings.make_commtime_function(comm_dict, known_shapes)

    assert isinstance(commtime(a, A, B), (int, float))
    assert commtime(a, A, B) == commtime(a, B, A)

    elemwise = e.owner
    dot = d.owner
    assert comptime(elemwise, A) == 1
    assert comptime(elemwise, B) == 100
    assert comptime(dot, A) == 100
    assert comptime(dot, B) == 1

    graphs, scheds, rankfile = distribute(inputs, outputs, input_shapes,
                                          machines, commtime, comptime, 50)

    # graphs == "{'A': ([b, a], [e]), 'B': ([a], [d])}"
    ais, [ao]  = graphs[A]
    [bi], [bo] = graphs[B]
    assert set(map(str, ais)) == set("ab")
    assert ao.name == e.name
    assert bi.name == a.name
    assert bo.name == d.name

    assert rankfile[A] != rankfile[B]
    assert str(scheds['B'][0]) == str(dot)
    assert map(str, scheds['A']) == map(str, (c.owner, e.owner))

    # test graphs, scheds, rankfile
    # test that inputs and outputs are untouched

    # Write to disk
    # write(graphs, scheds, rankfile, rootdir, known_shapes)

    # test files created
    # test that can read them correctly
