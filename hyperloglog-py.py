#!/usr/bin/env python3
"""HyperLogLog cardinality estimator."""
import sys,hashlib,math

class HyperLogLog:
    def __init__(self,p=14):
        self.p=p;self.m=1<<p;self.registers=[0]*self.m
        self.alpha={4:0.532,5:0.697,6:0.709}.get(p,0.7213/(1+1.079/self.m))
    def _hash(self,item):return int(hashlib.sha256(str(item).encode()).hexdigest(),16)
    def add(self,item):
        h=self._hash(item);idx=h&(self.m-1);w=h>>self.p
        self.registers[idx]=max(self.registers[idx],self._rho(w))
    def _rho(self,w):
        if w==0:return 64-self.p
        return (w&-w).bit_length()
    def count(self):
        Z=sum(2.0**(-r) for r in self.registers)
        E=self.alpha*self.m*self.m/Z
        if E<=2.5*self.m:
            V=self.registers.count(0)
            if V>0:E=self.m*math.log(self.m/V)
        return int(E)
    def merge(self,other):
        self.registers=[max(a,b)for a,b in zip(self.registers,other.registers)]

def main():
    if len(sys.argv)>1 and sys.argv[1]=="--test":
        hll=HyperLogLog(10)
        for i in range(10000):hll.add(f"item{i}")
        est=hll.count()
        assert 8000<est<12000,f"Bad estimate: {est} (expected ~10000)"
        # Duplicates shouldn't increase count
        for i in range(10000):hll.add(f"item{i}")
        est2=hll.count()
        assert abs(est-est2)<1000,f"Duplicates changed count: {est} vs {est2}"
        # Merge
        h1,h2=HyperLogLog(10),HyperLogLog(10)
        for i in range(5000):h1.add(i)
        for i in range(5000,10000):h2.add(i)
        h1.merge(h2)
        assert 8000<h1.count()<12000
        print("All tests passed!")
    else:
        hll=HyperLogLog()
        for i in range(100000):hll.add(i)
        print(f"HyperLogLog estimate: {hll.count()} (actual: 100000)")
if __name__=="__main__":main()
