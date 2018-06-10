from threading import Thread


class StoppableThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.stop = False

    def shutdown(self):
        self.stop = True

    def run(self):
        while not self.stop:
            self.do_run()
        self.finalize()

    def do_run(self):
        raise NotImplementedError

    def finalize(self):
        raise NotImplementedError

