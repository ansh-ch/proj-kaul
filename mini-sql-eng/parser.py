#!/usr/bin/env python
import sqlparse

def check(a, hai):
    return True

    b=False
    if a in hai:
        b= True
    else:
        b= False
    return b

def parse(tables, list_of_dics, sql_line):

    error_flag=0
    try:
        result=sqlparse.format(sql_line,keyword_case="lower")
        result=sqlparse.parse(result)

        stmt=result[0].tokens

    except:
        error_flag=-1
    

    i=0
    display_cols=[]
    sql_tables=[]
    sql_conds=[]
    sql_andor=""

    if 'select' in str(stmt[i]):
        i=i+1

        if ' ' in str(stmt[i]):
            i=i+1
            if len(str(stmt[i])) > 0 and check(str(stmt[i]), []):
                temp=str(stmt[i]).strip()
                temp=temp.replace(" ","")
                temp=temp.split(',')
                display_cols=temp
                i=i+1

                if ' ' in str(stmt[i]):
                    i=i+1
                    if 'from' in str(stmt[i]):
                        i=i+1
                        if ' ' in str(stmt[i]):
                            i=i+1
                            if len(str(stmt[i])) > 0 and check(str(stmt[i]), []):
                                temp=str(stmt[i]).strip()
                                temp.replace(" ",",")
                                temp=temp.split(',')
                                sql_tables=temp
                                i=i+1
                                if i < len(stmt) and ' ' in str(stmt[i]):
                                    i=i+1
                                    if len(str(stmt[i])) > 0 and check(str(stmt[i]), []):
                                        

                                        temp=str(stmt[i])
                                        if temp[0:5:1]=="where":
                                            temp=temp[5::]
                                            if " and " in temp:
                                                temp=temp.replace(" and " , ",")
                                                sql_andor="and"
                                            else:
                                                if " or " in temp:
                                                    temp=temp.replace(" or " , ",")
                                                    sql_andor="or"

                                            temp=temp.replace(" or " , ",")
                                            temp=temp=temp.replace(" ","")
                                            sql_conds=temp.split(",")
                                            i=100
                                    else:
                                        error_flag=-1
                                else:
                                    try:
                                        if ';' not in str(stmt[i]):
                                            error_flag=-1
                                    except:
                                        error_flag=-1
                                    
                            else:
                                error_flag=-1
                        else:
                            error_flag=-1
                    else:
                        error_flag=-1
                else:
                    error_flag=-1
            else:
                error_flag=-1
        else:
            error_flag=-1
    else:
        error_flag=-1

    if error_flag==-1:
        return ([],[],[],"")
        print "Error__ Syntax is rotten"
        return "Error__ Syntax is rotten"
    else:
        
        return (display_cols,sql_tables,sql_conds,sql_andor)
