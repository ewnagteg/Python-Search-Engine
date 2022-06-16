from time import sleep, time

class Timer():
    """
    Util Class for timing things
    Use:
    t = Timer()
    for i in range(replications):
        t.start('mark1')
        t.start('mark2')
        # do stuff
        t.end()
        t.end()
    t.compute()
    """
    def __init__(self):
        self._stack = []
        self._name_stack = []
        self._times = {}
        self._atimes = {}
        self._ncnt = {}
        self._nosleep = {}
        self._sleep = False
        self._sleep_mult = 1.05
        self._improve = None

    def start(self, name):
        self._stack.append(time())
        self._name_stack.append(name)
        if not name in self._times:
            self._times[name] = 0
            self._ncnt[name] = 0

    def end(self):
        name = self._name_stack.pop()
        if self._sleep and not name in self._nosleep:
            sleep(self._sleep_mult * self._atimes[name])
        start = self._stack.pop()
        self._times[name] += time() - start
        self._ncnt[name] += 1
    
    def compute(self, silent=False):
        for name in self._times:
            self._atimes[name] = self._times[name]/self._ncnt[name]
            if not silent:
                print(f'{name},{self._times[name]/self._ncnt[name]}')
        
    def compute_data(self):
        aves = {}
        for name in self._times:
            aves[name] = self._times[name]/self._ncnt[name]
        return aves

    def analyze(self, func, samps=30):
        # get names by calling func once, should have timer.start('mark') calls in it
        self._improve = {}
        total = 0
        for i in range(samps):
            s = time()
            func()
            e = time()
            total += e-s

        self.compute()