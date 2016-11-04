#!/usr/bin/env python
import parser
import limes
import runner

def loop():
    table=[]
    list_of_dics=[]
    sql_line=""
    (tables,list_of_dics)= limes.initialize()

    while 1:
        print "Wish?   "
        sql_line=raw_input()
        if sql_line=="quit":
            break
        else:

            display_cols=[]
            sql_tables=[]
            sql_conds=[]
            sql_andor=""
            try:
                (display_cols,sql_tables,sql_conds,sql_andor)= parser.parse(tables,list_of_dics,sql_line)
                runner.run(tables,list_of_dics,display_cols,sql_tables,sql_conds,sql_andor)      
            except:
                print "Error__ Rotten Syntax"

    
loop()

