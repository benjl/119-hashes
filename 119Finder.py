import hashlib as h
import time
import sys
from multiprocessing import Pool

# This is a really stupid program. It searches SHA256 hashes for 119s. 
# It puts the hashes in order of what ascii-encoded number produces them,
# then searches for the first hash that has a certain number of 119s in it.
# The first hash to contain a 119 is the hash of 78. The first hash to contain
# two 119s is hash 2707. From there the probability exponentially increases.
# The first triple 119 hash is 3283267. Approximately 1 in 2.2 million hashes
# (if I've done my math correctly) has three 119s in it. The first quad 119 is
# in hash 347477657. As of writing this, the first quint 119 hash has yet to be found.
# The probability of any hash being a quint 119 is about 1 in 365 billion.
# Again, assuming I've done the math right. https://www.desmos.com/calculator/ao0dnye9py

def leadingzeros(inp):
    n = 0
    for c in inp:
        if c == '0':
            n += 1
        else:
            break
    return n
    
def runs(inp, best): # Outputs the longest repetition length in the hash
    last = ""
    highest = 1
    n = 1
    for c in inp:
        if c == last:
            n += 1
            if n > highest:
                highest = n
        else:
            n = 1
        last = c
    return highest

def numberof119s(inp, best):
    # We include best because we can stop looking if there's no way the number can break the record
    # by a certain point. For example, if the best is 6, there needs to be at least one 119 in the
    # first 64-(3*6)=46 characters. If not, 
    n = 0
    d = 0
    end = -3*best if best > 0 else 64
    for c in inp[:end]:
        if d == 0:
            if c == '1':
                d = 1
            else:
                d = 0
        elif d == 1:
            if c == '1':
                d = 2
            else:
                d = 0
        elif d == 2:
            if c == '1':
                d = 2
            elif c == '9':
                d = 0
                n += 1
            else:
                d = 0
    if n >= 1 and best > 0:
        for c in inp[end:]:
            if d == 0:
                if c == '1':
                    d = 1
                else:
                    d = 0
            elif d == 1:
                if c == '1':
                    d = 2
                else:
                    d = 0
            elif d == 2:
                if c == '1':
                    d = 2
                elif c == '9':
                    d = 0
                    n += 1
                else:
                    d = 0
    return n
    
def numberof119s_old(inp, best):
    n = 0
    d = 0
    for c in inp:
        if d == 0:
            if c == '1':
                d = 1
            else:
                d = 0
        elif d == 1:
            if c == '1':
                d = 2
            else:
                d = 0
        elif d == 2:
            if c == '1':
                d = 2
            elif c == '9':
                d = 0
                n += 1
            else:
                d = 0
    return n

def batchtest(start, end, best): # Check for hashes with 119 and return any that have more than best 119s
    try:
        bests = []
        for n in range(start, end): # [start, end)
            hash = h.sha256(bytes(str(n), 'ascii')).hexdigest()
            zn = numberof119s(hash, best)
            if zn > best:
                bests.append((zn, n, hash))
        return bests
    except KeyboardInterrupt:
        return ['ki']

if __name__ == '__main__':
    n = 0
    best = 0
    bestn = 0
    besth = ''

    if len(sys.argv) > 1:
        if sys.argv[1] == 'resume':
            with open('savedprogress.txt', 'r') as f:
                for line in f:
                    if line[0] == 'n':
                        n = int(line[1:])
                    if line[0] == 'b':
                        best = int(line[1:])
                    if line[0] == 'z':
                        bestn = int(line[1:])
                    if line[0] == 'h':
                        besth = line[1:].strip('\n')
            print(f'Continuing from {n}, best @ {best}: {bestn} -> {besth}')

    b = 0
    t = 0
    avg = []
    batchsize = 2500000
        
    try:
        while best < 64: # Basically forever
            tick0 = time.time()
            results = []
            
            with Pool(processes=4) as pool:
                b1 = pool.apply_async(batchtest, (n,n+batchsize,best))
                b2 = pool.apply_async(batchtest, (n+batchsize,n+2*batchsize,best))
                b3 = pool.apply_async(batchtest, (n+2*batchsize,n+3*batchsize,best))
                b4 = pool.apply_async(batchtest, (n+3*batchsize,n+4*batchsize,best))
                
                results = b1.get() + b2.get() + b3.get() + b4.get()
            
            if "ki" in results:
                raise KeyboardInterrupt
            
            for r in results: # (119count, n, hash)
                if r[0] > best:
                    print(f'[{r[0]}] Hash of {r[1]}: {r[2]}')
                    if len(sys.argv) > 1:
                        if sys.argv[1] == 'resume':
                            with open('bests.txt', 'a') as f:
                                f.write(f'[{r[0]}] Hash of {r[1]}: {r[2]}\n')
                    best = r[0]
                    bestn = r[1]
                    besth = r[2]
            
            n += 4*batchsize # Number we're on
            b += 4*batchsize # Total in batch
            t += 4*batchsize # Total this session
            # Progress report
            tick1 = time.time()
            knps = b / ((tick1 - tick0) * 1000)
            avg.append(knps)
            if knps >= 1000:
                print(f'{round(knps/1000, 2)}M iter/s')
            else:
                print(f'{round(knps, 2)}K iter/s')
            b = 0
            tick0 = tick1
    except KeyboardInterrupt:
        if t >= 1000000:
            print(f'Numbers checked this time: {round(t/1000000, 2)}M')
        else:
            print(f'Numbers checked this time: {round(t/1000, 2)}K')
        if len(sys.argv) > 1:
            if sys.argv[1] == 'resume':
                with open('savedprogress.txt', 'w') as f:
                    print(f'Got to {n}, best {best} -> {besth}. Saving.')
                    print(f'Average speed: {round(sum(avg)/max(len(avg),1), 2)}K iter/s')
                    f.write(f'n{n}\n')
                    f.write(f'b{best}\n')
                    f.write(f'z{bestn}\n')
                    f.write(f'h{besth}\n')
                    sys.exit(1)
        print(f'Got to {n}, best {best} -> {besth}.')
        print(f'Average speed: {round(sum(avg)/max(len(avg),1), 2)}K iter/s')