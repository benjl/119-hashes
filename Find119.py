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
# in hash 347477657. As of writing this, the first quint 119 hash is 834152113309.
# The probability of any hash being a quint 119 is about 1 in 365 billion.
# Again, assuming I've done the math right. https://www.desmos.com/calculator/ao0dnye9py

def save_progress(n, best, bestn, besth, savefile=None):
    if savefile is None:
        savefile = 'savedprogress.txt'
    with open(savefile, 'w') as f:
        f.write(f'n{n}\n')
        f.write(f'b{best}\n')
        f.write(f'z{bestn}\n')
        f.write(f'h{besth}\n')

def collection(count, n, hash, savefile=None):
    if savefile is None:
        savefile = 'collection.txt'
    with open(savefile, 'a') as f:
        f.write(f'[{count}] {n} -> {hash}\n')

def load_progress(savefile=None):
    if savefile is None:
        savefile = 'savedprogress.txt'
    n = 0
    best = 0
    bestn = 0
    besth = ''
    with open(savefile, 'r') as f:
        for line in f:
            if line[0] == 'n':
                n = int(line[1:])
            if line[0] == 'b':
                best = int(line[1:])
            if line[0] == 'z':
                bestn = int(line[1:])
            if line[0] == 'h':
                besth = line[1:].strip('\n')
    return (n, best, bestn, besth)

def num_str(n): # 999 999.99K 999.99M 999.99B 999.99T
    out = ''
    if n >= 1000000000000:
        out = f'{round(n/1000000000000, 2)}T'
    elif n >= 1000000000:
        out = f'{round(n/1000000000, 2)}B'
    elif n >= 1000000:
        out = f'{round(n/1000000, 2)}M'
    elif n >= 1000:
        out = f'{round(n/1000, 2)}K'
    else:
        out = f'{round(n, 2)}'
    return out

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

def batchtest(start, end, best): # Check for hashes with 119 and return any that have more than best 119s
    try:
        bests = []
        for n in range(start, end): # [start, end)
            hash = h.sha256(bytes(str(n), 'ascii')).hexdigest()
            zn = hash.count('119')
            if zn > min(3, best): # Always report any quad+ 119s found
                bests.append((zn, n, hash))
        return bests
    except KeyboardInterrupt:
        return 'ki'

if __name__ == '__main__':
    save_mode = False
    collect_mode = False
    n = 0
    best = 0
    bestn = 0
    besth = ''

    if len(sys.argv) > 1:
        if 'resume' in sys.argv:
            save_mode = True
            collect_mode = True
            n,best,bestn,besth = load_progress()
            print(f'Continuing from {num_str(n)}, best [{best}] {bestn} -> {besth}')
        if 'collect' in sys.argv:
            print('Collection mode active')
            collect_mode = True

    workers = 4
    last_save = 0
    b = 0
    t = 0
    avg = []
    batchsize = 5000000
        
    try:
        while best < 21: # Basically forever
            tick0 = time.time()
            results = []
            batches = []
            with Pool(processes=workers) as pool:
                for w in range(workers):
                    batches.append(pool.apply_async(batchtest, (n+batchsize*w, n+batchsize*(w+1), best)))
                
                results = [x.get() for x in batches]
            
            if "ki" in results:
                raise KeyboardInterrupt
            for batch in results:
                for r in batch: # (119count, n, hash)
                    if r[0] > 3 and collect_mode: # Add notable quad+ 119s to The Collection
                        collection(r[0], r[1], r[2])
                    if r[0] > best:
                        print(f'New best: Found [{r[0]}] {r[1]} -> {r[2]}')
                        if save_mode:
                            with open('bests.txt', 'a') as f:
                                f.write(f'[{r[0]}] {r[1]} -> {r[2]}\n')
                        best = r[0]
                        bestn = r[1]
                        besth = r[2]
                    elif r[0] > 3:
                        print(f'Found [{r[0]}] {r[1]} -> {r[2]}')
            
            n += workers*batchsize # Number we're on
            b += workers*batchsize # Total in batch
            t += workers*batchsize # Total this session
            # Progress report
            tick1 = time.time()
            nps = b / (tick1 - tick0)
            avg.append(nps)
            if len(avg) > 2000:
                avg = avg[2000:]
            print(f'{num_str(t)} checked ({num_str(nps)} nps)')
            if t >= last_save + 1000000000 and save_mode: # Save progress every billion numbers
                print(f'Saving...')
                save_progress(n, best, bestn, besth)
                last_save = t
            b = 0
            tick0 = tick1
    except KeyboardInterrupt:
        print(f'Numbers checked this time: {num_str(t)}')
        if save_mode:
            print(f'Got to {num_str(n)}, best [{best}] {bestn} -> {besth}. Saving.')
            print(f'Average speed: {num_str(sum(avg)/max(len(avg),1))} nps')
            save_progress(n, best, bestn, besth)
            sys.exit(1)
        print(f'Got to {num_str(n)}, best [{best}] {bestn} -> {besth}.')
        print(f'Average speed: {num_str(sum(avg)/max(len(avg),1))} nps')