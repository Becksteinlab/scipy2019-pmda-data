import datreant as dtr
import pandas as pd
from pmda.util import make_balanced_slices
import numpy as np
import glob
import os

def conclude(total, io, compute, univ, w):
    '''Function to gather the total time, prepare time,
    universe time and maximum IO, computation, and wait time.

    total: path to the total benchmark data
    io: path to the io data
    compute: pate to the compute data
    '''
    data_t = np.loadtxt(total)
    all_io = np.loadtxt(io)
    all_compute = np.loadtxt(compute)
    all_univese = np.load(univ)
    all_wait = np.load(w)
    ndx = data_t[:,0]
    total = data_t[:,1]
    prepare = data_t[:,4]
    conclude = data_t[:,7]
    universe = []
    wait = []
    IO = []
    com = []
    stop = len(all_io[1,:])-1
    start = 0

    for i, j in enumerate(ndx):
        n_frames = len(all_io[1,:])
        n_blocks = int(j)
        slices = make_balanced_slices(n_frames, n_blocks,
                                  start=start, stop=stop, step=1)
        io_block = np.zeros(n_blocks)
        com_block = np.zeros(n_blocks)
        for k, bslice in enumerate(slices):
            k_io = all_io[i, bslice.start:bslice.stop]
            k_com = all_compute[i, bslice.start:bslice.stop]
            io_block[k] = np.sum(k_io)
            com_block[k] = np.sum(k_com)
        main = all_univese[i]+all_wait[i]+io_block+com_block
        n = np.argmax(main)
        IO.append(io_block[n])
        com.append(com_block[n])
        universe.append(all_univese[i][n])
        wait.append(all_wait[i][n])
    d = {'n': ndx, 'total': total, 'prepare': prepare, 'conclude': conclude,
         'universe': universe, 'wait': wait, 'IO': IO, 'compute': com}
    df = pd.DataFrame(data = d)
    return df

def mean_std(results):
    stat = pd.DataFrame([])
    ns = np.unique(results.n)
    for i in ns:
        i_df = results[results.n==i]
        IO = i_df.IO
        total = i_df.total
        pre = i_df.prepare
        con = i_df.conclude
        univ = i_df.universe
        wait = i_df.wait
        com = i_df.compute
        i_stat = {'n': i, 'total': total.mean(), 'total_std': total.std(),
                'IO': IO.mean(), 'IO_std': IO.std(),
                'prepare': pre.mean(), 'prepare_std': pre.std(),
                'conclude': con.mean(), 'conclude_std': con.std(),
                'universe': univ.mean(), 'universe_std': univ.std(),
                'wait': wait.mean(), 'wait_std': wait.std(),
                'compute': com.mean(), 'compute_std': com.std() }
        i_df = pd.DataFrame(i_stat, index=[1])
        stat = stat.append(i_df)
    stat.reset_index(drop=True)
    return stat


#Gathering Treants
b = dtr.discover()

#tags for Treants
source = ['Lustre', 'SSD']
size = ['9000', '900']
analysis = ['RDF', 'RMS']
scheduler = ['distr', 'multi']
nodes = ['3nodes', '6nodes']

# for Lustre distributed
for s in source:
    for n in size:
        print n
        for ana in analysis:
            print ana
            for sche in scheduler:
                print sche
                if (sche == 'distr') & (s == 'Lustre'):
                    for node in nodes:
                        print node
                        results = pd.DataFrame([])
                        t = b[b.tags[[n, node, ana]]]
                        for data in t.trees():
                            lvs = data.leaves()
                            total = lvs.globfilter('benchmark*')[0].abspath
                            io = lvs.globfilter('io*')[0].abspath
                            compute = lvs.globfilter('compute*')[0].abspath
                            univ = lvs.globfilter('universe*')[0].abspath
                            w = lvs.globfilter('wait*')[0].abspath
                            df = conclude(total, io, compute, univ, w)
                            results = results.append(df)
                        results.reset_index(drop=True)
                        path = os.path.join(t[0].abspath, 'conclusion.csv')
                        results.to_csv(path)
                        stat = mean_std(results)
                        spath = os.path.join(t[0].abspath, 'stat.csv')
                        stat.to_csv(spath)
                else:
                    results = pd.DataFrame([])
                    t = b[b.tags[[n, s, sche, ana]]]
                    for data in t.trees():
                        lvs = data.leaves()
                        total = lvs.globfilter('benchmark*')[0].abspath
                        io = lvs.globfilter('io*')[0].abspath
                        compute = lvs.globfilter('compute*')[0].abspath
                        univ = lvs.globfilter('universe*')[0].abspath
                        w = lvs.globfilter('wait*')[0].abspath
                        df = conclude(total, io, compute, univ, w)
                        results = results.append(df)
                    results.reset_index(drop=True)
                    path = os.path.join(t[0].abspath, 'conclusion.csv')
                    results.to_csv(path)
                    stat = mean_std(results)
                    spath = os.path.join(t[0].abspath, 'stat.csv')
                    stat.to_csv(spath)
