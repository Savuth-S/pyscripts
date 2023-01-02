import os
import time
"""Console Utils"""


def fnClear():
    if os.name in ("nt", "dos"):
        os.system('cls')
    else:
        os.system('clear')


def getNavCharacter():
    if os.name in ("nt", "dos"):
        return "\\"
    else:
        return "/"


def fnRenderProgressBar(nTotal, nProgress, nLenght=50):
    fPercent = ("{0:.1f}").format(100*(nProgress/float(nTotal)))
    nFilledLength = int(nLenght * nProgress//nTotal)
    sBar = ('█' * nFilledLength) + (' ' * (nLenght-nFilledLength))

    return f"|{sBar}| {fPercent}%"


class ETA:
    m_fElapsedTime = m_fStart = 0
    m_nTotal = m_nProgress = 1

    def __init__(self, nTotal):
        self.m_nTotal = nTotal

    def fnStart(self):
        self.m_fStart = time.perf_counter()

    def fnUpdate(self, nProgress=1):
        self.m_fElapsedTime += time.perf_counter()-self.m_fStart

        if (nProgress > 0 and self.m_nProgress != nProgress):
            self.m_nProgress = nProgress

    def fnRenderETA(self):
        nTimeLeft = int(((self.m_fElapsedTime*self.m_nTotal)/self.m_nProgress)-self.m_fElapsedTime)
        return f"ETA {nTimeLeft//60//60%60}h {nTimeLeft//60%60}m {nTimeLeft%60}s"
