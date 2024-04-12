from concurrent.futures import ThreadPoolExecutor


# pool of threads
class Threadpool:

    def __init__(self, NUM_OF_THREADS=1):
        self.executor = ThreadPoolExecutor(NUM_OF_THREADS)

    def submit_task(self, f, tmp, wallets):
        future = self.executor.submit(f, tmp, wallets)
        return future
