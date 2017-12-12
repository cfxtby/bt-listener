
import multiprocessing
import runPcap,ipTh,threading,gui

class runP(multiprocessing.Process):
    def run(self):
        sig=threading.Event()
        addth=ipTh.ipAddTh(sig)
        addth.start()

        run=runPcap.runPcap(sig)
        run.initial()
        run.run()

class runGui(multiprocessing.Process):
    def run(self):
        g=gui.gui()
        g.run()


if __name__=="__main__":
    g=runGui()
    g.start()

    sig = threading.Event()
    addth = ipTh.ipAddTh(sig)
    addth.start()

    run = runPcap.runPcap(sig)
    run.initial()
    run.run()
