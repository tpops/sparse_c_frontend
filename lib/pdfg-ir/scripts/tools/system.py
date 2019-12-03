import subprocess as sub

def run(cmd='', input='', sh=True, verbose=False):
    proc = sub.Popen(cmd, shell=sh, stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE)
    if len(input) > 0:
        data = proc.communicate(input=input.lstrip().encode('ascii'))
        output = data[0].decode()
        error = data[1].decode()
    else:
        output = proc.stdout.read().decode()
        error = proc.stderr.read().decode()
    if verbose:
        if len(output) > 0:
            print("Output:")
            print("================================================================================================\n")
            print(output)
        if len(error) > 0:
            print("Error:")
            print("================================================================================================\n")
            print(error)
    return (output, error)

def ncpus():
    n = 0
    try:
        import multiprocessing as mp
        n = mp.cpu_count()
    except (ImportError, NotImplementedError):
        n = 1

    return n

def threaded():
    try:
        import concurrent.futures
        return True
    except (ImportError, NotImplementedError):
        return False
