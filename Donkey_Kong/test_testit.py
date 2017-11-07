import donk
import firecoin
import purse
import pygame
import main
from pygame.locals import *
play=main.Board()
class Test_donkey():
    def test_donk(self):
        self.dragon=donk.Donkey('demon5.png',40,60,60,525)
        self.dragon.rect.x=self.dragon.rect.x +10
        self.lim=self.dragon.limit()
        assert self.dragon.rect.x>=self.lim[0]
        assert self.dragon.rect.x<=self.lim[1]        
        
class Test_player():
    def test_limit(self):
        self.god=purse.Player()
        self.lim=self.god.limit()
        for i in range(5):
            assert self.god.rect.x>=self.lim[0]
            assert self.god.rect.x<=self.lim[1]
            self.god.rect.x=self.god.rect.x-10
            self.god.check()
        assert self.god.rect.x>= self.lim[0]
        assert self.god.rect.x<= self.lim[1]        

        self.god.rect.x=585
        for i in range(5):
            assert self.god.rect.x>= self.lim[0]
            assert self.god.rect.x<= self.lim[1]            
            self.god.rect.x=self.god.rect.x-10
            self.god.check()
        assert self.god.rect.x>= self.lim[0]
        assert self.god.rect.x<= self.lim[1]
        
    def test_collide_donk(self):
        self.d_list=pygame.sprite.Group()
        self.god=purse.Player()
        self.god.rect.x=40
        self.dragon=donk.Donkey('demon5.png',40,60,60,525)
        self.d_list.add(self.dragon)
        self.hit_list=pygame.sprite.spritecollide(self.god,self.d_list,False)
        assert len(self.hit_list)>0
        self.god.rect.x=150
        self.hit_list=[]
        self.hit_list=pygame.sprite.spritecollide(self.god,self.d_list,False)
        assert len(self.hit_list)==0
        
    def test_collide_fire(self):
        self.f_list=pygame.sprite.Group()
        self.god=purse.Player()
        self.god.rect.x=40
        self.hellfire=firecoin.Fireball(40,535,'fireball.png')
        self.f_list.add(self.hellfire)
        self.hit_list=pygame.sprite.spritecollide(self.god,self.f_list,False)
        self.hit_list=[]
        assert len(self.hit_list)==0
        for i in range(7):
            self.god.rect.x=self.god.rect.x + 5
            if len(pygame.sprite.spritecollide(self.god,self.f_list,False)) > 0:
                self.hit_list=pygame.sprite.spritecollide(self.god,self.f_list,False)
        
        assert len(self.hit_list)>0

    def test_collide_ladder(self):
        self.god=purse.Player()
        self.god.rect.x=20
        assert self.god.ladder()==0
        self.god.rect.x=365
        assert self.god.ladder()>0

class Test_Coin():
    def test_generate_coins(self):
        self.c_list=pygame.sprite.Group()
        self.i=0
        for self.i in range(6):
            self.c_list.add(firecoin.Coin(545,5,588))
        self.i=0
        for self.i in range(6):
            self.c_list.add(firecoin.Coin(445,5,405))
        assert len(self.c_list) == 12

class Test_requirements():
    def test_score(self):
        self.c_list=pygame.sprite.Group()
        self.god=purse.Player()
        self.god.rect.x=0
        self.god.change_score(0)
        self.hit_list=[]
        self.i=0
        for self.i in range(6):
            self.c_list.add(firecoin.Coin(545,10,300))
        while self.god.rect.x < 320:
            self.god.rect.x=self.god.rect.x + 3
            if len(pygame.sprite.spritecollide(self.god,self.c_list,False)) > 0:
                self.god.change_score(self.god.get_score() + 25)
        assert self.god.get_score >=125

    def test_lives(self):
        self.player=purse.Player()
        assert self.player.get_life() == 3
        self.player.change_life(self.player.get_life() - 1)
        assert self.player.get_life() == 2
