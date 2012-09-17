from sys import argv, stdout, stdin, stderr
import theano
import time
from ape.timings.computation.run import debugprint, collect_inputs, comptime_run
from ape.timings.theano_gpu_util import cpu_to_gpu_graph, togpu_data

def time_computation(inputs, outputs, numeric_inputs, niter):

    gpu_inputs, gpu_outputs = cpu_to_gpu_graph(inputs, outputs)
    gpu_numeric_inputs = map(togpu_data, numeric_inputs)

    f = theano.function(gpu_inputs, gpu_outputs)

    starttime = time.time()
    debugprint("Computing")
    for n in xrange(niter):
        outputs = f(*numeric_inputs)
    endtime = time.time()
    duration = endtime - starttime

    return duration/niter

if __name__ == '__main__':

    known_shapes, niter, fgraphs = collect_inputs(argv, stdin)
    results = comptime_run(known_shapes, niter, fgraphs, time_computation)

    stdout.write(str(results))
    stdout.close()

