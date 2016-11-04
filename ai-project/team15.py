import operator
import copy
import timeit
import random

def find_bells(temp_board, mov):
	id1 = mov[0]/3
	id2 = mov[1]/3
	beells = []

	for i in range(id1*3,id1*3+3):
		for j in range(id2*3,id2*3+3):
			beells.append(temp_board[i][j])
	return beells

class Player15:
	
	def __init__(self):
		# You may initialize your object here and use any variables for storing throughout the game
		self.counter = 0;
		self.yolo = 4
		self.time = 0
		self.time_flag=0
		pass

	def move(self,temp_board,temp_block,old_move,pl_flag):
		total_block_value = [0,0,0,0,0,0,0,0,0]
		time = timeit.default_timer()
		self.time_flag = 0
		if old_move == (-1,-1) :
			cls = [(3,3),(3,5),(5,3),(5,5)]
			go_cell = cls[random.randrange(4)]
			total_block_value=find_new_blist(go_cell, temp_board,"max",total_block_value,pl_flag,0)
			self.counter = 1
			# print "blist is ", total_block_value

		else :
			self.counter +=2
			alpha = -10000000000000000
			beta = 100000000000000000
			
			if self.counter >= 30 :
				self.yolo = 6

			if self.counter >=50:
				self.yolo = 8
			blocks_allowed  = determine_blocks_allowed(old_move, temp_block)
			
			cells = get_empty_out_of(temp_board, blocks_allowed,temp_block)
			
			if old_move!= (-1,-1) :
				total_block_value=find_new_blist(old_move, temp_board,"max",total_block_value,pl_flag,0)


		
			copy_blist = copy.deepcopy(total_block_value)
			# copy_temp_board = copy.deepcopy(temp_board)
			copy_temp_block = copy.deepcopy(temp_block)

			depth = 1
			turn = "max"
			time_flag = 0
			time = timeit.default_timer()
			(huristics,go_cell,returnedvalue) = self.min_max(temp_board,copy_temp_block,old_move,depth,turn,copy_blist,pl_flag,alpha,beta,time)
		
		return go_cell

	def min_max(self,temp_board,temp_block,old_move,depth,turn,copy_blist,pl_flag,alpha,beta,time):

		if depth == self.yolo:
			# print depth
			if pl_flag == "x":
				op_flag = "o"
			else :
				op_flag = "x"
			copy_blist=find_new_blist(old_move, temp_board ,turn,copy_blist, op_flag ,1)

			heuris = heuroh(old_move,temp_block,copy_blist,op_flag,turn)
			
			return (heuris,old_move,heuris)
		
		else :

			if depth != 1:
				if turn == "max":
					turrn = "opp"

				else :
					turrn = "meeeeeeeeee"

				temp='x'
				if turn== "min":
					if pl_flag =='x':
						temp='o'

		
				copy_blist=find_new_blist(old_move, temp_board ,turn,copy_blist, temp ,1)

		
			cop_blist = copy.deepcopy(copy_blist)
			# copy_board = copy.deepcopy(temp_board)
			copy_block = copy.deepcopy(temp_block)

			blocks_allowed  = determine_blocks_allowed(old_move, copy_block)
			cells = get_empty_out_of(temp_board, blocks_allowed,copy_block)

			
			select_list = {}
			# print cells
			op_flag = '-'	
			if pl_flag == "x":
				op_flag = "o"
			else :
				op_flag = "x"

			if turn == "max": 
				for cell in cells:
					if alpha > beta :
						break
					cop_blist = copy.deepcopy(copy_blist)
					# copy_board = copy.deepcopy(temp_board)
					copy_block = copy.deepcopy(temp_block)
					pts = update_temp_lists(temp_board,copy_block,cell,pl_flag)
					new_time = timeit.default_timer()
					(huristic_value,go_cell,returnedvalue) = self.min_max(temp_board,copy_block,cell,depth + 1,"min",cop_blist,op_flag,alpha,beta,new_time)
				
					temp_board[cell[0]][cell[1]] = '-'
					
					if returnedvalue > alpha:
						alpha = returnedvalue

					select_list[huristic_value] = cell
					if new_time - time > 5:
						break
				
				if len(select_list) == 0 :
					
					if turn == "max" :
						# heuris = heuroh(old_move,copy_block,cop_broben,copy_blist,bells,op_flag, turn)
						heuris = -5000
					elif turn == "min":
						heuris = heuroh(old_move,copy_block,copy_blist,op_flag, turn)
					return (heuris,old_move,heuris)
				else :
					ans = max(select_list.iteritems(), key=operator.itemgetter(0)) 
					ans += (alpha,)
					return ans

			elif turn == "min":
				for cell in cells :
					if alpha > beta :
						break
					cop_blist = copy.deepcopy(copy_blist)
					# copy_board = copy.deepcopy(temp_board)
					copy_block = copy.deepcopy(temp_block)

					
					pts = update_temp_lists(temp_board,copy_block,cell,pl_flag)

					new_time = timeit.default_timer()
					(huristic_value,go_cell,returnedvalue) = self.min_max(temp_board,copy_block,cell,depth + 1,"max",cop_blist,op_flag,alpha,beta,new_time)
					temp_board[cell[0]][cell[1]] = '-'

					if returnedvalue < beta:
						beta = returnedvalue

					select_list[huristic_value] = cell
					if new_time - time > 5:
						break
				if len(select_list) == 0 :
					
					if turn == "max" :
						# heuris = heuroh(old_move,copy_block,cop_broben,copy_blist,bells,op_flag, turn)
						heuris = -5000
					elif turn == "min":
						heuris = heuroh(old_move,copy_block,copy_blist,op_flag, turn)
					# heuris = heuroh(old_move,copy_block,cop_broben,copy_blist,bells,op_flag,turn)
					return (heuris,old_move,heuris)	
				else :
					ans = min(select_list.iteritems(), key=operator.itemgetter(0))
					ans += (beta,)
					return ans
		

def find_new_blist(old_move ,temp_board ,playerz ,blist, pl_fl, initial):
	if initial ==0 :

                lister=[(0,0),(0,3),(0,6),(3,0),(3,3),(3,6),(6,0),(6,3),(6,6)]
                blist=[0,0,0,0,0,0,0,0,0]
                k=0
                for i in lister:
                    bells=find_bells(temp_board,i)
                    s=eight(old_move, bells, pl_fl, 1)
                    if s is not None:
                        for j in s[0]:
                            blist[k]+=j
                    k=k+1

                # print "for initial", blist

                return blist


	else :
           
		summ=0
		# min means my turn

		bells=find_bells(temp_board,old_move)
		s=eight(old_move, bells, pl_fl, 1)
		if s is not None:
			for j in s[0]:
				summ+=j
			blist[(old_move[0]/3+1)*3-3+old_move[1]/3]= summ 

		return blist

def heuroh(cell,temp_block,copy_blist, pl_fl, turn ):

	cube_allowed=[]

	x= cell[0]
	y= cell[1]

	if x % 3 == 0 and y % 3 == 0:
		cube_allowed = [1,3]
	elif x % 3 == 0 and y % 3 == 2:
		cube_allowed = [1,5]
	elif x % 3 == 2 and y % 3 == 0:
		cube_allowed = [3,7]
	elif x % 3 == 2 and y % 3 == 2:
		cube_allowed = [5,7]
	elif x % 3 == 0 and y % 3 == 1:
		cube_allowed = [0,2]
	elif x % 3 == 1 and y % 3 == 0:
		cube_allowed = [0,6]
	elif x % 3 == 2 and y % 3 == 1:
		cube_allowed = [6,8]
	elif x % 3 == 1 and y % 3 == 2:
		cube_allowed = [2,8]
	elif x % 3 == 1 and y % 3 == 1:
		cube_allowed = [4]


	x= x/3
	y=y/3
	bsum=0
	miin=90000
	maax= -90000

	for i in copy_blist:
		bsum+=i
		if i<miin:
			miin=i
		if i>maax:
			maax=i

	mid=bsum/9

	rel_cell = [cell[0]%3,cell[1]%3]

	a1=0
	for i in copy_blist:
		if turn=="min":
			a1+=i

		if turn=="max":
			a1=a1-i

 

	c=eight([x,y], temp_block, pl_fl, 0)

	sum2=0

	for i in c[0]:
		sum2+=i

	# print a1

	final= 10*a1 + 10000*sum2




	return final

def eight(mov, bells, pl_fl, block_or_board):

	bigben=[6,3,6,3,1,3,6,3,6]

	if pl_fl=='x':
		pl2_fl='o'
	else:
		pl2_fl='x'

	res=[0,0,0,0,0,0,0,0]
	cno= 0
	rno=0
	ret2=0
	ret31=[]
	ret32=[]
	fret31=[]
	fret32=[]

	win1=[]
	win2=[]
	x1=0
	o1=0
	x2=0
	o2=0

	j=0

	for cno in range(3):
	    rno=(cno+1)*3 -3
	    z1=1;z2=1
	    flag1=0;flag2=0
	    j=0
	    x1=0;o1=0;x2=0;o2=0
	    while j<=2:


	        if bells[rno+j]==pl_fl:
	            x=1
	            x1=x1+1
	            if rno+j==4:
	    			flag1=1
	        if bells[rno+j]==pl2_fl:
	            x=-1
	            o1=o1+1
	            if rno+j==4:
	    			flag1=1
	        if bells[rno+j]=='D':
	    		x=0
	    		z1=0
	        if bells[rno+j]=='-':
	            x=0    
	            ret31.append(rno+j)

	    
	    	if cno+3*j==4:
	    		flag2=1

	        if bells[cno+3*j]==pl_fl:
	            y=1
	            x2=x2+1
	            if cno+3*j==4:
	    			flag2=1
	        if bells[cno+3*j]==pl2_fl:
	            y=-1
	            o2=o2+1
	            if cno+3*j==4:
	    			flag2=1
	        if bells[cno+3*j]=='-':
	            y=0
	            ret32.append(cno+3*j)
	        if bells[cno+3*j]=='D':
	            y=0 
	            z2=0             
	            
	        j=j+1

	 	
	    res[cno]= 1 * (10**x1) + -1* (6**o1)

	    if o1==2 and x1==1:
	        res[cno]= 1 * (10**x1) + 1 * 400

	    if (x1!=3 and flag1==1 and block_or_board==1):
	    	res[cno]= 0
	    elif (o1!=3 and flag1==1 and block_or_board==1):
	    	res[cno]=0



	    res[cno+3]= 1 * (10**x2) + -1* (6**o2)

	    if o2==2 and x2==1:
	        res[cno+3]= 1 * (10**x2) + 1 * 400

	    if (x2!=3 and flag2==1 and block_or_board==1):
	    	res[cno+3]= -100
	    elif (o2!=3 and flag2==1  and block_or_board==1):
	    	res[cno+3]= -100

	            

	    if(o1==2 and x1==0):
	        ret2= 3000
	        fret31+=ret31
	    
	    if(o1==0 and x1==2):
	        ret2= 90000
	        fret32+=ret31

	    if(o2==2 and x2==0):
	        if ret2!=90000:
	            ret2= 3000
	        fret31+=ret32
	        
	    if(o2==0 and x2==2):
	        ret2= 90000
	        fret32+=ret32
            
    
	x1=0
	o1=0
	i=0
	j=0; ret31=[];ret32=[]
	flag1=0

	listup=[0,4,8]
	for i in listup:
	    if bells[i]==pl_fl:
	        x=1
	        x1=x1+1
	        if i==4:
	    		flag1=1
	    if bells[i]==pl2_fl:
	        x=-1
	        o1=o1+1
	        if i==4:
	    		flag1=1
	    if bells[i]=='-':
	        x=0                                  
	        ret31.append(i)

	res[6]= 1 * (10**x1) + -1* (6**o1) 


	if o1==2 and x1==1:
	    res[6]= 1 * (10**x1) + 1 * 400

	if (x1!=3 and flag1==1 and block_or_board==1):
	   	res[6]=0
	elif (o1!=3 and flag1==1 and block_or_board==1):
	    res[6]=0
				

	if(o1==2 and x1==0):
	    if ret2!=90000:
	        ret2= 3000
	    fret31+=ret31
	if(o1==0 and x1==2):
	    ret2= 90000
	    fret32+=ret31

	x1=0
	o1=0; ret31=[]
	flag1=0

	listup=[2,4,6]
	for i in listup:
	    if bells[i]==pl_fl:
	        x=1
	        x1=x1+1
	        if i==4:
	    		flag1=1
	    if bells[i]==pl2_fl:
	        x=-1
	        o1=o1+1
	        if i==4:
	    		flag1=1
	    if bells[i]=='-':
	        x=0                       
	        ret31.append(i)
	res[7]= 1 * (10**x1) + -1* (6**o1)

	if o1==2 and x1==1:
	    res[7]= 1 * (10**x1) + 1 * 400

	if (x1!=3 and flag1==1 and block_or_board==1):
	   	res[7]=0
	elif (o1!=3 and flag1==1 and block_or_board==1):
	    res[7]=0
	    
	if(o1==2 and x1==0):
	    if ret2!=90000:
	        ret2= 3000
	    fret31+=ret31
	if(o1==0 and x1==2):
	    ret2= 90000
	    fret32+=ret31

	return [res ,fret31,fret32]

def determine_blocks_allowed(old_move, block_stat):
	blocks_allowed = []
	if old_move == (-1,-1):
		blocks_allowed = [0,1,2,3,4,5,6,7,8]
	else :
		if old_move[0] % 3 == 0 and old_move[1] % 3 == 0:
			blocks_allowed = [1,3]
		elif old_move[0] % 3 == 0 and old_move[1] % 3 == 2:
			blocks_allowed = [1,5]
		elif old_move[0] % 3 == 2 and old_move[1] % 3 == 0:
			blocks_allowed = [3,7]
		elif old_move[0] % 3 == 2 and old_move[1] % 3 == 2:
			blocks_allowed = [5,7]
		elif old_move[0] % 3 == 0 and old_move[1] % 3 == 1:
			blocks_allowed = [0,2]
		elif old_move[0] % 3 == 1 and old_move[1] % 3 == 0:
			blocks_allowed = [0,6]
		elif old_move[0] % 3 == 2 and old_move[1] % 3 == 1:
			blocks_allowed = [6,8]
		elif old_move[0] % 3 == 1 and old_move[1] % 3 == 2:
			blocks_allowed = [2,8]
		elif old_move[0] % 3 == 1 and old_move[1] % 3 == 1:
			blocks_allowed = [4]
		else:
			sys.exit(1)
	final_blocks_allowed = []
	for i in blocks_allowed:
		if block_stat[i] == '-':
			final_blocks_allowed.append(i)
	return final_blocks_allowed

def get_empty_out_of(gameb, blal,block_stat):
	cells = []  # it will be list of tuples
	#Iterate over possible blocks and get empty cells
	for idb in blal:
		id1 = idb/3
		id2 = idb%3
		for i in range(id1*3,id1*3+3):
			for j in range(id2*3,id2*3+3):
				if gameb[i][j] == '-':
					cells.append((i,j))

	# If all the possible blocks are full, you can move anywhere
	if cells == []:
		new_blal = []
		all_blal = [0,1,2,3,4,5,6,7,8]
		for i in all_blal:
			if block_stat[i]=='-':
				new_blal.append(i)

		for idb in new_blal:
			id1 = idb/3
			id2 = idb%3
			for i in range(id1*3,id1*3+3):
				for j in range(id2*3,id2*3+3):
					if gameb[i][j] == '-':
						cells.append((i,j))
	return cells


def update_temp_lists(temp_board, temp_block, cell, pl_flag):

	temp_board[cell[0]][cell[1]] = pl_flag

	block_no = (cell[0]/3)*3 + cell[1]/3	
	id1 = block_no/3
	id2 = block_no%3
	mflg = 0

	flag = 0
	for i in range(id1*3,id1*3+3):
		for j in range(id2*3,id2*3+3):
			if temp_board[i][j] == '-':
				flag = 1



	if temp_block[block_no] == '-':
		if temp_board[id1*3][id2*3] == temp_board[id1*3+1][id2*3+1] and temp_board[id1*3+1][id2*3+1] == temp_board[id1*3+2][id2*3+2] and temp_board[id1*3+1][id2*3+1] != '-' and temp_board[id1*3+1][id2*3+1] != 'D':
			mflg=1
		if temp_board[id1*3+2][id2*3] == temp_board[id1*3+1][id2*3+1] and temp_board[id1*3+1][id2*3+1] == temp_board[id1*3][id2*3 + 2] and temp_board[id1*3+1][id2*3+1] != '-' and temp_board[id1*3+1][id2*3+1] != 'D':
			mflg=1
		if mflg != 1:
                    for i in range(id2*3,id2*3+3):
                        if temp_board[id1*3][i]==temp_board[id1*3+1][i] and temp_board[id1*3+1][i] == temp_board[id1*3+2][i] and temp_board[id1*3][i] != '-' and temp_board[id1*3][i] != 'D':
                                mflg = 1
                                break
		if mflg != 1:
                    for i in range(id1*3,id1*3+3):
                        if temp_board[i][id2*3]==temp_board[i][id2*3+1] and temp_board[i][id2*3+1] == temp_board[i][id2*3+2] and temp_board[i][id2*3] != '-' and temp_board[i][id2*3] != 'D':
                                mflg = 1
                                break
	if mflg == 1:
		temp_block[block_no] = pl_flag

        if flag == 0 and mflg == 0 :
                temp_block[block_no] = 'D'

	return mflg

def update_lists(game_board, block_stat, move_ret, fl):

	game_board[move_ret[0]][move_ret[1]] = fl

	block_no = (move_ret[0]/3)*3 + move_ret[1]/3	
	id1 = block_no/3
	id2 = block_no%3
	mflg = 0

	flag = 0
	for i in range(id1*3,id1*3+3):
		for j in range(id2*3,id2*3+3):
			if game_board[i][j] == '-':
				flag = 1

	if flag == 0:
		block_stat[block_no] = 'D'

	if block_stat[block_no] == '-':
		if game_board[id1*3][id2*3] == game_board[id1*3+1][id2*3+1] and game_board[id1*3+1][id2*3+1] == game_board[id1*3+2][id2*3+2] and game_board[id1*3+1][id2*3+1] != '-' and game_board[id1*3+1][id2*3+1] != 'D':
			mflg=1
		if game_board[id1*3+2][id2*3] == game_board[id1*3+1][id2*3+1] and game_board[id1*3+1][id2*3+1] == game_board[id1*3][id2*3 + 2] and game_board[id1*3+1][id2*3+1] != '-' and game_board[id1*3+1][id2*3+1] != 'D':
			mflg=1
		if mflg != 1:
                    for i in range(id2*3,id2*3+3):
                        if game_board[id1*3][i]==game_board[id1*3+1][i] and game_board[id1*3+1][i] == game_board[id1*3+2][i] and game_board[id1*3][i] != '-' and game_board[id1*3][i] != 'D':
                                mflg = 1
                                break
		if mflg != 1:
                    for i in range(id1*3,id1*3+3):
                        if game_board[i][id2*3]==game_board[i][id2*3+1] and game_board[i][id2*3+1] == game_board[i][id2*3+2] and game_board[i][id2*3] != '-' and game_board[i][id2*3] != 'D':
                                mflg = 1
                                break
	if mflg == 1:
		block_stat[block_no] = fl
	
	return mflg
