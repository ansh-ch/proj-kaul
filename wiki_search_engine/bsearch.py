import os
import json
import re
import math
import time
import multiprocessing
import heapq
from operator import itemgetter

dic_id = {}
dic_titles = {}
dirr = "res_ind/dum"
champSubSize = 20
champMainSize = 20
idf = []
total_no_docs = 0
threads = 2

stop_words = {'a':1,'about':1,'above':1,'across':1,'after':1,'afterwards':1,'again':1,'against':1,'all':1,'almost':1,'alone':1,'along':1,'already':1,'also':1,'although':1,'always':1,'am':1,'among':1,'amongst':1,'amoungst':1,'amount':1,'an':1,'and':1,'another':1,'any':1,'anyhow':1,'anyone':1,'anything':1,'anyway':1,'anywhere':1,'are':1,'around':1,'as':1,'at':1,'back':1,'be':1,'became':1,'because':1,'become':1,'becomes':1,'becoming':1,'been':1,'before':1,'beforehand':1,'behind':1,'being':1,'below':1,'beside':1,'besides':1,'between':1,'beyond':1,'bill':1,'both':1,'bottom':1,'but':1,'by':1,'call':1,'can':1,'cannot':1,'cant':1,'co':1,'con':1,'could':1,'couldnt':1,'cry':1,'de':1,'describe':1,'detail':1,'do':1,'done':1,'down':1,'due':1,'during':1,'each':1,'eg':1,'eight':1,'either':1,'eleven':1,'else':1,'elsewhere':1,'empty':1,'enough':1,'etc':1,'even':1,'ever':1,'every':1,'everyone':1,'everything':1,'everywhere':1,'except':1,'few':1,'fifteen':1,'fify':1,'fill':1,'find':1,'fire':1,'first':1,'five':1,'for':1,'former':1,'formerly':1,'forty':1,'found':1,'four':1,'from':1,'front':1,'full':1,'further':1,'get':1,'give':1,'go':1,'had':1,'has':1,'hasnt':1,'have':1,'he':1,'hence':1,'her':1,'here':1,'hereafter':1,'hereby':1,'herein':1,'hereupon':1,'hers':1,'herself':1,'him':1,'himself':1,'his':1,'how':1,'however':1,'hundred':1,'ie':1,'if':1,'in':1,'inc':1,'indeed':1,'interest':1,'into':1,'is':1,'it':1,'its':1,'itself':1,'keep':1,'last':1,'latter':1,'latterly':1,'least':1,'less':1,'ltd':1,'made':1,'many':1,'may':1,'me':1,'meanwhile':1,'might':1,'mill':1,'mine':1,'more':1,'moreover':1,'most':1,'mostly':1,'move':1,'much':1,'must':1,'my':1,'myself':1,'name':1,'namely':1,'neither':1,'never':1,'nevertheless':1,'next':1,'nine':1,'no':1,'nobody':1,'none':1,'noone':1,'nor':1,'not':1,'nothing':1,'now':1,'nowhere':1,'of':1,'off':1,'often':1,'on':1,'once':1,'one':1,'only':1,'onto':1,'or':1,'other':1,'others':1,'otherwise':1,'our':1,'ours':1,'ourselves':1,'out':1,'over':1,'own':1,'part':1,'per':1,'perhaps':1,'please':1,'put':1,'rather':1,'re':1,'same':1,'see':1,'seem':1,'seemed':1,'seeming':1,'seems':1,'serious':1,'several':1,'she':1,'should':1,'show':1,'side':1,'since':1,'sincere':1,'six':1,'sixty':1,'so':1,'some':1,'somehow':1,'someone':1,'something':1,'sometime':1,'sometimes':1,'somewhere':1,'still':1,'such':1,'system':1,'take':1,'ten':1,'than':1,'that':1,'the':1,'their':1,'them':1,'themselves':1,'then':1,'thence':1,'there':1,'thereafter':1,'thereby':1,'therefore':1,'therein':1,'thereupon':1,'these':1,'they':1,'thickv':1,'thin':1,'third':1,'this':1,'those':1,'though':1,'three':1,'through':1,'throughout':1,'thru':1,'thus':1,'to':1,'together':1,'too':1,'top':1,'toward':1,'towards':1,'twelve':1,'twenty':1,'two':1,'un':1,'under':1,'until':1,'up':1,'upon':1,'us':1,'very':1,'via':1,'was':1,'we':1,'well':1,'were':1,'what':1,'whatever':1,'when':1,'whence':1,'whenever':1,'where':1,'whereafter':1,'whereas':1,'whereby':1,'wherein':1,'whereupon':1,'wherever':1,'whether':1,'which':1,'while':1,'whither':1,'who':1,'whoever':1,'whole':1,'whom':1,'whose':1,'why':1,'will':1,'with':1,'within':1,'without':1,'would':1,'yet':1,'you':1,'your':1,'yours':1,'yourself':1,'yourselves':1,'the':1,'\'':1,'mdy':1,'ebg':1,'eba':1,'ebc':1,'ebm':1,'ebn':1,'ebo':1,'ebi':1,'ebj':1,'ebt':1,'ebu':1,'ebv':1,'ebp':1,'ebr':1,'ebx':1}


def bin_search(word, fileName):
    bytess = os.path.getsize(fileName)

    with open(fileName, "r") as fp:
        left, right = 0, bytess - 1 
        key = None
        while key != word and left <= right:
            mid = (left + right) / 2
            fp.seek(mid)
            # now realign to a record
            if mid:
                fp.readline()
                
            (key, value) = parseLine(fp.readline())
            #print (key, word,value), (left,right, mid)
            
            if word > key:
                left = mid + 1
            else:
                right = mid - 1
        if key != word:
            value = None # for when search key is not found
        return (key, value) # store the result of the search

    
def parseLine(line):
    return (line[:line.find(":")], line[line.find(":") +1 :])

    
def process_word(word):
    global dirr
    ls = ["0-1-2-3-4-5-6-7-8-9","a-b", "c-d", "e-f", "g-h", "i-j", "k-l","m-n", "o-p", "q-r", "s-t", "u-v", "w-x", "y-z"]
    fileName = ""
    for i in ls:
        if word[0] in i.split("-"):
            fileName = dirr+"/"+i
            break

    return bin_search(word, fileName)


def beginParallel(func, arg):
    start_time = time.time()
    #print  multiprocessing.current_process().name, "starts\n"
    content = func(arg)
    return [content, time.time()-start_time, multiprocessing.current_process().name]


def getKey(item):
    return item[0]
        

def mergeAlgo(ls):

    if ls[1] == None:
        return ls[0]
    
    global champMainSize
    result = []
    l = ls[0]
    m = ls[1]
    i = j = 0
    total = len(l) + len(m)
    while len(result) < champMainSize and len(result) < total:
        if len(l) == i:
            result += m[j: champMainSize - len(result) + j]
            break
        elif len(m) == j:
            result += l[i: champMainSize - len(result) + i]
            break
        elif l[i][0] > m[j][0]:
            result.append(l[i])
            i += 1
        else:
            result.append(m[j])
            j += 1
    return result

def merge(listFront):
    
    global threads

    while len(listFront) > 1:

        tasks = []
        mparallel = []
        size = len(listFront)/2

        for i in range(0, len(listFront), 2):
            ls = [listFront[i], listFront[i+1] if (i+1) < len(listFront) else None]
            mparallel.append(ls)

        pool = multiprocessing.Pool(threads)
        tasks = [(mergeAlgo, i) for i in mparallel]
        results = [pool.apply_async(beginParallel, t) for t in tasks]

        new_listFront = []
        for result in results:
            ls = result.get()
            new_listFront.append(ls[0])
            #print("%s completed, took %d seconds\n" % (ls[2], ls[1] ))

        listFront = new_listFront
        #print "New front : ",listFront, len(listFront)

        pool.close()
        pool.join()

    return listFront


def parseStruct(item, invdf):

    b = [float(item[item.find("b")+1:]), item.find("b")] if item.find("b") >= 0 else [0,-1]
    t = 0
    if b[1] >= 0:
        t = [float(item[item.find("t")+1: b[1]]), item.find("t")] if item.find("t")>=0 else [0,-1]
    else:
        t = [float(item[item.find("t")+1:]), item.find("t")]

    torf = t[1]
    if t[1] == -1:
        torf = b[1]

    doc_id = item[:torf]
    tf = 1+math.log(float(b[0])+t[0]*2.5)
    tf_idf = tf * math.log(float(total_no_docs)/invdf)

    return [tf_idf, doc_id]


def simpleSort(ls):
    final = []
    global idf
    global dic_id
    prev = 0
    for i in ls:
        pair = parseStruct(i, idf[-1])
        pair[1] = str(int(pair[1]) + prev)
        final.append(pair)
        prev = int(pair[1])
    
    final = sorted(final, key=getKey, reverse = True)
    return final[:champSubSize]
    

def final_choice(champs, freq_query):
    global dic_titles
    global champMainSize
    dtemp = {}
    for i in range(len(champs)):
        for j in champs[i].keys():
            if j not in dtemp:
                dtemp[j] = 0
            dtemp[j] += champs[i][j]*freq_query[i]
                
            for k in range(len(champs)):
                if champs[k]!= i and j in champs[k]:                    
                    dtemp[j] += champs[k][j]*freq_query[k]

    dtemp = heapq.nlargest(champMainSize, dtemp.items(), key = itemgetter(1))

    return dtemp
        

def process_query(query):

    exp_split = "\s|\-|T:|B:"
    query = filter(None, re.split( exp_split, query))
    query = [item.lower() for item in query]

    global stop_words
    global idf
    global threads

    champ_dics = []
    freq_query = []
    
    for i in query:
        if i not in stop_words:
            (key, value) = process_word(i)
            if value !=  None:
                freq_query.append( float(query.count(i))/len(query) )
                tasks = []
                value = value.split("*")
                value[-1] = value[-1][:value[-1].rfind("#")]
                total_occurence = 0
                for j in range(len(value)):
                    value[j] = value[j].split("|")
                    total_occurence += len(value[j])

                old_len = len(value)

                idf.append(total_occurence)

        
                pool = multiprocessing.Pool(threads)
                tasks = [(simpleSort, i) for i in value]
                results = [pool.apply_async(beginParallel, t) for t in tasks]

                sortedList = []
                for result in results:
                    ls = result.get()
                    sortedList.append(ls[0])
                    #print("%s sorted, took %d seconds\n" % (ls[2], ls[1] ))
        
                pool.close()
                pool.join()

                sortedList = merge(sortedList)
                sortedList = sortedList[0]
                dic = {}
                #print sortedList
                for j in sortedList:
                    #print j[1],j[0]
                    dic[j[1]] = j[0]
                
                champ_dics.append(dic)
                
    return final_choice(champ_dics, freq_query)
    
    
def run():
    global dic_id
    global dic_titles
    global idf
    global total_no_docs
    #open("../doc_ID_40.json", "r") as fp1,
    with  open("doc_titles_128.json", "r") as fp2:
        #dic_id = json.loads(fp1.read())
        dic_titles = json.loads(fp2.read())
        total_no_docs = len(dic_titles.keys())

    while True:
        print "\nInput Query :"
        q = raw_input()
        idf = []
        start_time = time.time()
        final = process_query(q)
        print "\n"
        for i in final:
            print dic_titles[i[0]], "       -------------       ",i[1]
        print "\nQuery time:  "+str(time.time() - start_time)+"  seconds"
run()
