from kazoo.client import KazooClient
# from kazoo.handlers.gevent import SequentialGeventHandler
import logging
import time
logging.basicConfig()
from config import nodes

zk = KazooClient(hosts='compute31:2182')


def experiment():
    current_time = time.time()
    counter = 0
    while time.time()-current_time < 10:
        zk.set('/mynode', '1'*1024)
        counter += 1
    print counter

def main():
    zk.start()
    if not zk.exists('/mynode'):
        zk.create("/mynode", "a value")
    experiment()
    return

if __name__ == "__main__":
    main()

