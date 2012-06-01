from mpi4py import MPI
import theano
from env_manip import unpack_many
import numpy as np

def host_name():
    import os
    return os.popen('uname -n').read().strip()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
host = host_name()
def exchange_ranks():
    names = comm.alltoall([host]*size)
    return dict(zip(names, range(comm.Get_size())))

# Perform handshake
rank_of_machine = exchange_ranks()

# Wrap MPI calls
send_requests = dict()
recv_requests = dict()
def send(var, tag, dest_machine_id):
    request = comm.isend(var, rank_of_machine[dest_machine_id], tag)
    send_requests[tag, dest_machine_id] = request
def recv(var, tag, source_machine_id):
    request = comm.irecv(var, rank_of_machine[source_machine_id], tag)
    recv_requests[tag, source_machine_id] = request
def wait_on_send(tag, id):
    send_requests[tag, id].wait()
def wait_on_recv(tag, id):
    recv_requests[tag, id].wait()

env_file = open("%(env_filename)s", 'r')
envs = unpack_many(env_file)
env_file.close()

mode = theano.compile.mode.get_default_mode()
# Compile Theano Functions
%(compile)s

# Initialize variables
%(variable_initialization)s

# Compute
%(host_code)s
