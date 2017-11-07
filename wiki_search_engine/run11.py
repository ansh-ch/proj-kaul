import os
import json
#import nltk
import re
#from nltk.stem import PorterStemmer
#from nltk.stem import SnowballStemmer
#from nltk.tokenize import word_tokenize
#import Stemmer
import time
import sys, collections
from struct import pack, unpack
#import itertools
#import dumpjson


def readJson(foil):

    json_list = []
    with open(foil) as json_file:
        json_list = json.loads(json_file.read())["wikidump"]

    return json_list


def findSubString(ls, sub):
    ind = [ls.index(s) for s in ls  if sub in s][0]
    ls[ind] = sub + "b"+str(int( ls[ind][ls[ind].find("b")+1:] ) + 1)
    return "|".join(ls)

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def saveIndex(index, out_file):
    print "gonna print in "+ out_file
    out_file= str(out_file)
    if not os.path.exists(os.path.dirname(out_file)):
        try:
            os.makedirs(os.path.dirname(out_file))
        except OSError as exc: # Guard against race condition
            print exc
            
    encode_lambda = (lambda n: str(n) if vb_encode(n).find("\n") >= 0 else vb_encode(n))
    with open(out_file, 'a') as fp:
        for key in index.keys():
            if isEnglish(key) == True:
                #fp.write( key.encode('utf-8')+":"+index[key][1] + "#" + encode_lambda(index[key][0]) +"\n")
                fp.write( key.encode('utf-8')+":"+index[key][1] + "#" + str(index[key][0]) +"\n")



def vb_encode(number):
    bytes = []
    while True:
        bytes.insert(0, number % 128)
        if number < 128:
            break
        number /= 128
    bytes[-1] += 128
    return pack('%dB' % len(bytes), *bytes)


def createIndex( final, json_data):

    relevant = ["text", "title"]
    
    stop_words = {'a':1,'about':1,'above':1,'across':1,'after':1,'afterwards':1,'again':1,'against':1,'all':1,'almost':1,'alone':1,'along':1,'already':1,'also':1,'although':1,'always':1,'am':1,'among':1,'amongst':1,'amoungst':1,'amount':1,'an':1,'and':1,'another':1,'any':1,'anyhow':1,'anyone':1,'anything':1,'anyway':1,'anywhere':1,'are':1,'around':1,'as':1,'at':1,'back':1,'be':1,'became':1,'because':1,'become':1,'becomes':1,'becoming':1,'been':1,'before':1,'beforehand':1,'behind':1,'being':1,'below':1,'beside':1,'besides':1,'between':1,'beyond':1,'bill':1,'both':1,'bottom':1,'but':1,'by':1,'call':1,'can':1,'cannot':1,'cant':1,'co':1,'con':1,'could':1,'couldnt':1,'cry':1,'de':1,'describe':1,'detail':1,'do':1,'done':1,'down':1,'due':1,'during':1,'each':1,'eg':1,'eight':1,'either':1,'eleven':1,'else':1,'elsewhere':1,'empty':1,'enough':1,'etc':1,'even':1,'ever':1,'every':1,'everyone':1,'everything':1,'everywhere':1,'except':1,'few':1,'fifteen':1,'fify':1,'fill':1,'find':1,'fire':1,'first':1,'five':1,'for':1,'former':1,'formerly':1,'forty':1,'found':1,'four':1,'from':1,'front':1,'full':1,'further':1,'get':1,'give':1,'go':1,'had':1,'has':1,'hasnt':1,'have':1,'he':1,'hence':1,'her':1,'here':1,'hereafter':1,'hereby':1,'herein':1,'hereupon':1,'hers':1,'herself':1,'him':1,'himself':1,'his':1,'how':1,'however':1,'hundred':1,'ie':1,'if':1,'in':1,'inc':1,'indeed':1,'interest':1,'into':1,'is':1,'it':1,'its':1,'itself':1,'keep':1,'last':1,'latter':1,'latterly':1,'least':1,'less':1,'ltd':1,'made':1,'many':1,'may':1,'me':1,'meanwhile':1,'might':1,'mill':1,'mine':1,'more':1,'moreover':1,'most':1,'mostly':1,'move':1,'much':1,'must':1,'my':1,'myself':1,'name':1,'namely':1,'neither':1,'never':1,'nevertheless':1,'next':1,'nine':1,'no':1,'nobody':1,'none':1,'noone':1,'nor':1,'not':1,'nothing':1,'now':1,'nowhere':1,'of':1,'off':1,'often':1,'on':1,'once':1,'one':1,'only':1,'onto':1,'or':1,'other':1,'others':1,'otherwise':1,'our':1,'ours':1,'ourselves':1,'out':1,'over':1,'own':1,'part':1,'per':1,'perhaps':1,'please':1,'put':1,'rather':1,'re':1,'same':1,'see':1,'seem':1,'seemed':1,'seeming':1,'seems':1,'serious':1,'several':1,'she':1,'should':1,'show':1,'side':1,'since':1,'sincere':1,'six':1,'sixty':1,'so':1,'some':1,'somehow':1,'someone':1,'something':1,'sometime':1,'sometimes':1,'somewhere':1,'still':1,'such':1,'system':1,'take':1,'ten':1,'than':1,'that':1,'the':1,'their':1,'them':1,'themselves':1,'then':1,'thence':1,'there':1,'thereafter':1,'thereby':1,'therefore':1,'therein':1,'thereupon':1,'these':1,'they':1,'thickv':1,'thin':1,'third':1,'this':1,'those':1,'though':1,'three':1,'through':1,'throughout':1,'thru':1,'thus':1,'to':1,'together':1,'too':1,'top':1,'toward':1,'towards':1,'twelve':1,'twenty':1,'two':1,'un':1,'under':1,'until':1,'up':1,'upon':1,'us':1,'very':1,'via':1,'was':1,'we':1,'well':1,'were':1,'what':1,'whatever':1,'when':1,'whence':1,'whenever':1,'where':1,'whereafter':1,'whereas':1,'whereby':1,'wherein':1,'whereupon':1,'wherever':1,'whether':1,'which':1,'while':1,'whither':1,'who':1,'whoever':1,'whole':1,'whom':1,'whose':1,'why':1,'will':1,'with':1,'within':1,'without':1,'would':1,'yet':1,'you':1,'your':1,'yours':1,'yourself':1,'yourselves':1,'the':1,'\'':1,'mdy':1,'ebg':1,'eba':1,'ebc':1,'ebm':1,'ebn':1,'ebo':1,'ebi':1,'ebj':1,'ebt':1,'ebu':1,'ebv':1,'ebp':1,'ebr':1,'ebx':1}


    #!!!!!!!!!!!  below statement unable to remove escape from final index 
    exp_words = "&|http|\?|File:|\\|.com"
    exp_split = "Category:|=|\.|\||\!|#|_|\-|\n|:"
    lambdaz = [(lambda s: "t"+str(s) if s>0  else ""), (lambda s: "b"+str(s) if s>0  else ""),
                   (lambda s: s[:s.find["g"]] if s.find("g")>=0 else s[:s.find("b")])]
    #  &nbsp
    #stemmer = Stemmer.Stemmer("english")
    
    for dic in json_data:
        
        perDoc = {}
        
        
        for key in relevant:
            dic[key] = filter(None, re.split("\s|;|,|\"|\(|\)|\'|\*|\[\[|\]\]|\[|\]|" + exp_split, dic[key]))
            #print "\nBEEEEE 4    \n", dic[key]
            #dic[key] = filter(None , map((lambda d: "" if bool(re.search(exp_words , d))==True else d), dic[key]))
            #print "\nClEANED 4    \n", dic[key]
            #dic[key] = sum(map((lambda d: filter(None, re.split(exp_split, d))), dic[key]), [])

            for word in dic[key]:
                vurd = word.lower()
                #vurd = stemmer.stemWord(vurd)
                
                if vurd not in stop_words:
                    if vurd not in perDoc:
                        if key == "text":
                            perDoc[vurd] = {"text":1, "title":0}
                        else:
                            perDoc[vurd] = {"text":0, "title":1}

                    else:
                        perDoc[vurd][key] += 1
                

        for each in perDoc:
            encoded_id = 0
            if each in final:
                gap = int(dic["id"]) - final[each][0]
                final[each][0] = int(dic["id"])
                
                temp = vb_encode(gap)
                if str(temp).find("\n") >= 0 :
                    encoded_id = str(gap)
                else:
                    encoded_id = temp
                    
                encoded_id = str(gap)
                final[each][1] = final[each][1] + "|" + encoded_id + lambdaz[0](perDoc[each]["title"]) + lambdaz[1](perDoc[each]["text"])

            else:
                temp = vb_encode(int(dic["id"]))
                if str(temp).find("\n") >= 0 :
                    encoded_id = str(dic["id"])
                else:
                    encoded_id = temp
                encoded_id = str(dic["id"])
                final[each] = [int(dic["id"]) ,encoded_id + lambdaz[0](perDoc[each]["title"]) + lambdaz[1](perDoc[each]["text"])]

    #stroll = json_data[1234]["text"]
    #print [m.start() for m in re.finditer("outfielders", " ".join(stroll))]
    #outfielders : d2241-t0b3|d2366-t0b1|d2427-t0b1|d2532-t0b2|d4089-t0b1
    return final


def search(s):
    #print "Searching~~\n"
    tokens= word_tokenize(s)
    tokens = [item.lower() for item in tokens]
    ps = PorterStemmer()
    tokens = [ps.stem(item) for item in tokens]
    print tokens
    
    
def run(ls):

    midSource = ls[0]
    dest = ls[1]
    start_time = time.time()
    #sys.argv[1] and sys.argv[2]
    final = {}
    for one in midSource:
        
        json_data = readJson(one)
        #json_data = json_data["wikidump"]
    
        final = createIndex(final, json_data)

    final = collections.OrderedDict(sorted(final.items()))
    saveIndex(final, dest)
    
    print "---  " + str(time.time() - start_time) + "  seconds  ---"
    '''
    s = raw_input("Search? ")
    while(s != "quit()"):
        search(s)
        s = raw_input("Search? ")
    '''
