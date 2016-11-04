#!/usr/bin/env python


# Makes dictionary tables


def initialize() :

    flag=0
    try:
        meta=open("metadata.txt","r")
    except IOError as e:
        print e
        flag=1

    if flag==0:
        reed=meta.readlines()
        meta.close()
        tables=[]
        list_of_dics=[]
        get_cols=0
        ls_cols=[]
        dic={}
        count=0
        for s in reed:
            if get_cols==1 and s!="<end_table>\r\n":

                dic={}
                tables.append(s[0:s.find("\r\n"):1])
                get_cols=2
                col_file=open( str(tables[-1])+".csv" , "r")
                kilua=col_file.readlines()
                col_file.close()

                arow=kilua[0]
                arow=arow[0:arow.find("\r\n"):1]
                commasplit=arow.split(",")
                ls_cols=[]

                for j in commasplit:
                    ls_cols.append([j])


                for i in range(1, len(kilua)):
                    arow=str(kilua[i])
                    arow=arow[0:arow.find("\r\n"):1]
                    commasplit=arow.split(",")

                    for k in range(0, len(commasplit)):
                        ls_cols[k].append(commasplit[k])

            else:
                if get_cols==2 and s!="<end_table>\r\n" and s!="<end_table>":
                    s=s[0:s.find("\r\n"):1]
                    dic[s]=ls_cols[count]
                    count=count+1

                else:
                    if s=="<end_table>\r\n" or s=="<end_table>":
                        get_cols=0
                        count=0
                        list_of_dics.append(dic)

            if s=="<begin_table>\r\n":
                get_cols=1

        return (tables,list_of_dics)
