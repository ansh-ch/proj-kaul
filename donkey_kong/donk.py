import purse
from random import randint
import firecoin
class Donkey(purse.Person):
    def __init__(self,s,b,l,x,y):
        purse.Person.__init__(self)
        self.makechar(s,b,l,x,y)
        self.__dcount=150

    def moveslikejagger(self,f_list,s,y_ahoo):
        if self.__dcount<=0:
            self.__dcount=151
        elif self.__dcount<=75:
            self.rect.x-=5
        elif self.__dcount>75:
            if self.rect.x>=590:
                self.__dcount=75
            else:
                self.rect.x +=5
	self.no=randint(30,40)
        if self.__dcount %self.no ==0:
            self.fire=firecoin.Fireball(self.rect.x,y_ahoo,s)
            f_list.add(self.fire)
        self.__dcount-=1
        return f_list
