import os
from pyrrd.rrd import DataSource, RRA, RRD
from time import time

from kernelhive.monitoring import MonitoringHandler


# TODO: dirty fast code, refactor
class RRDHandler(MonitoringHandler):
    def __init__(self, rrd_dir):
        self.rrd_dir = rrd_dir
        self.rrds = dict()

    def create_rrd(self, gpuid):
        ret = RRD('/'.join([self.rrd_dir, '%s.rrd' % gpuid]),
                       ds=[DataSource(dsName='utilization', dsType='GAUGE', heartbeat=10)],
                       rra=[RRA(cf='MIN', xff=0.5, steps=1, rows=360)],
                       step=10,
                       start=int(time())
                       )
        ret.create()
        return ret

    def handle_monitoring(self, infrastructure):
        for node in infrastructure.keys():
            node_data = infrastructure[node]
            if 'gpu' in node_data.keys():
                for gpu_id in node_data['gpu'].keys():
                    if gpu_id not in self.rrds.keys():
                        self.rrds[gpu_id] = self.create_rrd(gpu_id)
                    if 'utilization' in node_data['gpu'][gpu_id].keys():
                        self.rrds[gpu_id].bufferValue(time(), node_data['gpu'][gpu_id]['utilization'])
                        self.rrds[gpu_id].update()
