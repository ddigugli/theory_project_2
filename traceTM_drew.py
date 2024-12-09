import os
import csv

def parse(filename):
    # parse the ntm definition from a csv file
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File '{filename}' not found.")
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        headers = [next(reader) for _ in range(7)]
        transitions = {}
        for row in reader:
            state, char, newst, write, move = row
            key = (state, char.strip())
            if key not in transitions:
                transitions[key] = []
            transitions[key].append((newst, write.strip(), move.strip()))
        return headers, transitions

def sim_ntm(filename, inputstr, maxdep=10, maxtrans=100, outfilepath="output_drew.txt"):
    headers, transitions = parse(filename)      # simulates a ntm with bfs
    machine = headers[0][0]
    startst = headers[4][0]
    accst = headers[5][0]
    rejst = headers[6][0]

    def writeout(msg):              # writes output to file and prints to console
        with open(outfilepath, "a") as outfile:
            outfile.write(msg + '\n')
        print(msg)  # prints to terminal for live tracking
    writeout(f"{filename} is being processed with input: {inputstr}")       # log init details
    writeout(f"machine being used is, {machine}")
    writeout(f"input string is, {inputstr}")
    if not inputstr.strip():
        writeout("string rejected, input is empty, does not satisfy language")
        writeout("depth of tree of configurations: 0")
        writeout("total transitions simulated: 0")
        return False
    tree = [[("", startst, inputstr)]]     # bfs simulation beginning
    totaltrans = 0
    visitedconfigs = set()
    reachaccept = False

    def calc_ndm(tree):
        totconfigs = sum(len(level) for level in tree)      # calculates nondeterminism as average branching factor
        depth = len(tree)
        return totconfigs / depth if depth > 0 else 0
    for depth in range(maxdep):
        currlvl = tree[-1]
        nxtlvl = []
        anypathcontinue = False
        writeout(f"\ndepth {depth}:")
        for config in currlvl:
            left, state, right = config
            totaltrans += 1
            writeout(f"[{left}], ({state}), [{right}]")
            if config in visitedconfigs:
                continue
            visitedconfigs.add(config)
            if state == accst:            # accept cond. accept if we reach accst, even if tape not empty
                if not right or right == "_":  # accept even if tape not empty, no further moves
                    reachaccept = True
                    tree.append([config])  # st accepting config
                    break
            if state == rejst:              # reject state condition
                writeout(f"string rejected at state, {state}.")
                continue
            char = right[0] if right else '_'
            if (state, char) in transitions:
                for newst, write, move in transitions[(state, char)]:
                    # moves!!!
                    if move == 'R':
                        updateleft = left + write
                        updateright = right[1:]
                    elif move == 'L':
                        updateleft = left[:-1] if left else ''
                        updateright = (left[-1] if left else '') + write + right[1:]
                    else:
                        updateleft = left
                        updateright = write + right[1:]
                    newconfig = (updateleft, newst, updateright)
                    if newconfig not in visitedconfigs:
                        nxtlvl.append(newconfig)
                        anypathcontinue = True
        if reachaccept:                 # write results to output file
            nondeterminism = calc_ndm(tree)
            writeout(f"depth of config tree: {depth + 1}")
            writeout(f"total transitions simulated: {totaltrans}")
            writeout(f"degree of ndm: {nondeterminism:.2f}")
            writeout(f"string accepted in {depth + 1} transitions\n\n")
            return True
        if not anypathcontinue:         # write results to output file
            writeout(f"depth of config tree: {depth + 1}")
            writeout(f"total transitions simulated: {totaltrans}")
            writeout(f"degree of ndm: {calc_ndm(tree):.2f}")
            writeout("string rejected.\n\n")
            return False
        if depth < maxdep:          # check is exceeding dep
            tree.append(nxtlvl)
    writeout("execution stopped, hit max depth")        # if hit max dep stop
    writeout(f"depth of config tree: {maxdep}")
    writeout(f"total transitions simulated: {totaltrans}")
    writeout(f"degree of ndm: {calc_ndm(tree):.2f}")
    return False

def processcsvfiles():  # process many csv files and run ntm sim
    csv_files = [
        ("abc_star_drew.csv", "abcabab"),
        ("abc_star_drew.csv", "abc"),
        ("aplus_drew.csv", "y"),
        ("aplus_drew.csv", "aaaaa"),
    ]
    with open("output_drew.txt", "w") as outfile:       # clean output file before starting
        outfile.write("")                           # clean up any existing stuff
    for csv_file, inputstr in csv_files:        # run sim
        sim_ntm(csv_file, inputstr, maxdep=10)
        with open("output_drew.txt", "a") as outfile:
            outfile.write("\n\n")  # print blank at end of test case

# main func
if __name__ == "__main__":
    processcsvfiles()