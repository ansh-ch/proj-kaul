import os
import sys, time
import run11
import multiprocessing

def createJsonWiki(xmlPath):
    #dumpjson.main_dumper(xmlPath)
    #os.system('python ./wikiextractor-master/WikiExtractor.py --json --no-templates -o - -q ' +xmlPath+' > json.txt')
    os.system('python WikiExtractor.py --json --no-templates -q ' +xmlPath)


def beginParallel(func, arg):
    start_time = time.time()
    print  multiprocessing.current_process().name, "starts\n"
    func(arg)
    return (multiprocessing.current_process().name, time.time()-start_time, arg)
    
    
def parallel_run():
    xmlPath = str(sys.argv[1])
    createJsonWiki(xmlPath)
    
    division_size = 10
    
    
    files = [[],[]]
    total_file_count = 0
    division_count = 0
    files[0] = sorted(os.listdir("text"))
    parallel_read = []
    div_list = []
    
    for i in files[0]:
        files[1] = os.listdir("text/"+i)
        files[1].sort(key=lambda f: int(filter(str.isdigit, f)))
        for j in files[1]:
            total_file_count += 1
            temp = j[ j.find("_")+ 1: ]
            div_list.append("text/"+i+"/"+j)
            division_count+=1
            if division_count % division_size == 0:
                parallel_read.append([div_list, "res_ind/temp_"+ str(division_count/division_size)])
                div_list = []

    if len(div_list) > 0:
        parallel_read.append([div_list, "res_ind/temp_"+ str((division_count/division_size)+1)])
        div_list = []

    threads = 2
    pool = multiprocessing.Pool(threads)
    tasks = [(run11.run, i) for i in parallel_read]
    results = [pool.apply_async(beginParallel, t) for t in tasks]

    for result in results:
        (name, thread_time, agro) = result.get()
        print("%s completed, took %d seconds\n %s\n\n" % (name, thread_time, str(agro)))

    pool.close()
    pool.join()


start_time = time.time()
parallel_run()
print " T O T A L   ---  " + str(time.time() - start_time) + "  seconds  ---\n"
