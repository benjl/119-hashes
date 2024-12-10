import hashlib as h
import time
import sys

def leadingzeros(inp):
    n = 0
    for c in inp:
        if c == '0':
            n += 1
        else:
            break
    return n

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
tick0 = time.time()
avg = []
batchsize = 1000000
    
try:
    while best < 64: # Basically forever
        tick1 = time.time()
        for _ in range(batchsize):
            hash = h.sha256(bytes(str(n), 'ascii')).hexdigest()
            zn = numberof119s(hash, best)
            if zn > best:
                print(f'[{zn}] Hash of {n}: {hash}')
                best = zn
                bestn = n
                besth = hash
            n += 1
            b += 1
            t += 1
        # Progress report
        tick2 = time.time()
        avg.append(batchsize / ((tick2 - tick1) * 1000))
        if tick1-tick0 >= 30:
            knps = b / ((tick2 - tick0) * 1000)
            avg.append(knps)
            print(f'{round(knps, 2)}K iter/s')
            b = 0
            tick0 = tick2
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