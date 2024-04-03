from concurrent.futures import ThreadPoolExecutor


# pool of threads (use for mining, broadcast, etc)
class Threadpool:

    def __init__(self, NUM_OF_THREADS=1):
        self.executor = ThreadPoolExecutor(NUM_OF_THREADS)

    #TODO: should we delete the utxos and change it to sth else?
    def submit_task(self, f, tmp, utxos):
        future = self.executor.submit(f, tmp, utxos)
        return future
