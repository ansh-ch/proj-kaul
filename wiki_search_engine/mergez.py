import os
from struct import pack, unpack
import multiprocessing
import time


#Global variables
dirr = ""


def vb_decode(bytestream):
    n = 0
    numbers = []
    bytestream = unpack('%dB' % len(bytestream), bytestream)
    for byte in bytestream:
        if byte < 128:
            n = 128 * n + byte
        else:
            n = 128 * n + (byte - 128)
            numbers.append(n)
            n = 0
    return numbers


def vb_encode(number):
    bytes = []
    while True:
        bytes.insert(0, number % 128)
        if number < 128:
            break
        number /= 128
    bytes[-1] += 128
    return pack('%dB' % len(bytes), *bytes)


def mergeAlgo(fayls):
    alternate = ["temp", "bemp"]
    out_file = "anomaly"
    if fayls[0].find("temp") >= 0:
        out_file = dirr+"bemp_"+fayls[0].split("/")[-1][fayls[0].split("/")[-1].find("_")+1:]
    else:
        out_file = dirr+"temp_"+fayls[0].split("/")[-1][fayls[0].split("/")[-1].find("_")+1:]

    if fayls[1] == None:
        os.rename(fayls[0], out_file)
        return out_file.split("/")[-1]

    with open(fayls[0], "r") as a, open(fayls[1], "r") as b, open (out_file, "w") as out:
        line1 = a.readline()
        line2 = b.readline()
        while True:
            if line1 == "" or line2 == "":
                break
            decide = new_compareLine(line1, line2)
            if decide[0] == "n":
                line1 = a.readline()
            if decide[1] == "n":
                line2 = b.readline()

            out.write(decide[2])

        if line1 != "" and line2 == "":
            line1 = a.readline() 
            while line1 != "":
                out.write(line1)
                line1 = a.readline() 

        if line2 != "" and line1 == "":
            line2 = b.readline() 
            while line2 != "":
                out.write(line2)
                line2 = b.readline() 

    return out_file.split("/")[-1]


def new_compareLine(line1, line2):
    line1 = line1.strip()
    line2 = line2.strip()
    if line1[:line1.find(":")] == line2[:line2.find(":")]:
        new_line = line1[:line1.rfind("#")]+"*"+line2[line2.find(":")+1:]+"\n"
        return ["n", "n", new_line]

    else:
        if line1[:line1.find(":")] < line2[:line2.find(":")]:
            return ["n", "s", line1+"\n"]
        else:
            return ["s", "n", line2+"\n"]

def compareLine(line1, line2):
    line1 = line1.strip()
    line2 = line2.strip()
    if line1[:line1.find(":")] == line2[:line2.find(":")]:
        number = line1[ line1.rfind("#")+1:]
        temp = vb_decode(number)
        ls = parseLine(line2[line2.find(":")+1:])
        first_num = ls[0]
        diff = -1
        if len(temp) == 0:
            #print "roar"
            diff = first_num - int(number)
            #print "door"
        else:
            diff = first_num - temp[0]

        diff = vb_encode(diff) if vb_encode(diff).find("\n") == "-1" else str(diff)
        new_line = line1[:line1.rfind("#")]+"|"+diff+line2[line2.find(":")+ls[1]+1:]+"\n"
        
        return ["n", "n", new_line]

    else:
        if line1[:line1.find(":")] < line2[:line2.find(":")]:
            return ["n", "s", line1+"\n"]
        else:
            return ["s", "n", line2+"\n"]
            
def parseLine(line2):
    index = line2.find("t") if (line2.find("t") < line2.find("b") and line2.find("t") > -1) else line2.find("b")
    number = line2[:index]
    temp = vb_decode(number)
    if len(temp) == 0:
        return [int(number),index]
    else:
        return [temp[0], index]
    
#mergeAlgo(["res_ind/temp_1", "res_ind/temp_2"])
    
def beginParallel(func, arg):
    start_time = time.time()
    print  multiprocessing.current_process().name, "starts\n"
    new_file = func(arg)
    return [new_file, time.time()-start_time, multiprocessing.current_process().name]

def divide_index(acc_index):
    
    ls = ["0-1-2-3-4-5-6-7-8-9","a-b", "c-d", "e-f", "g-h", "i-j", "k-l","m-n", "o-p", "q-r", "s-t", "u-v", "w-x", "y-z"]

    with open(acc_index, "r") as a:
        for i in ls:
            if not os.path.exists(os.path.dirname(dirr+i)):
                try:
                    os.makedirs(os.path.dirname(dirr+i))
                except OSError as exc: # Guard against race condition
                    print exc

            with open(dirr+i, "w") as sub_file:
                mark = i.split("-")                
                line = a.readline()
                while line[0] not in mark:
                    line = a.readline()
                while line[0] in mark:
                    sub_file.write(line)
                    line = a.readline()


def parallel_merge():
    directory = raw_input()
    global dirr
    directory = directory+"/"
    dirr = directory
    fileFront = os.listdir(directory)
    fileFront.sort(key=lambda f: int(filter(str.isdigit, f)))
    while len(fileFront)>1:
        
        tasks = []
        mparallel = []
        size = len(fileFront)/2

        for i in range(0, len(fileFront), 2):
            ls = [directory+fileFront[i], directory+fileFront[i+1] if (i+1) < len(fileFront) else None]
            mparallel.append(ls)

        threads = 2
        pool = multiprocessing.Pool(threads)
        tasks = [(mergeAlgo, i) for i in mparallel]
        results = [pool.apply_async(beginParallel, t) for t in tasks]

        new_fileFront = []
        for result in results:
            ls = result.get()
            new_fileFront.append(ls[0])
            print("%s completed, took %d seconds\n" % (ls[2], ls[1] ))

        for j in fileFront:
            try:
                os.remove(directory+j)
            except:
                pass

        fileFront = new_fileFront
        fileFront.sort(key=lambda f: int(filter(str.isdigit, f)))
        #fileFront = sorted(fileFront)
        print "New : ",fileFront
            
        pool.close()
        pool.join()

    divide_index( directory+fileFront[0])
    #try:
    #    os.remove(directory+fileFront[0])
    #except:
    #    pass

start_time1 = time.time()        
parallel_merge()
print "---T O T A L--------(merge-divide)---"+str(start_time1-time.time())+"   seconds-----------\n"
