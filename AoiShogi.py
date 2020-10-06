import threading as th
import sys
sys.setrecursionlimit(1000000)

from copy import copy,deepcopy
from time import time,sleep
from random import choice,shuffle,randint

import tkinter.messagebox
from tkinter.filedialog import asksaveasfilename as askF
from tkinter import *

from Shogi import *
from ShogiObj import *



pl_icon = ('☖','☗')
class AoiShogi:
	def __init__(self,size=150):
		self.game = Shogi()
		self.pl = 1
		self.player = ['pl','pl']
		
		self.last_his = None
		self.first_his = None
		
		self.game_thread = None
		self.semi_thread = None
		
		self.sur = False
		self.state = ''
		self.temp = {}
		
		self.on = False
		self.w,self.h = size*15,size*9+20
		self.unit = size
		self.tk = Tk()
		self.tk.geometry(f'{self.w}x{self.h}')
		self.tk.resizable(height = 0, width = 0)
		self.tk.title("AoiShogi")
		self.tk.configure(bg='white')
		
		self.canvas = Canvas(self.tk, bd=1, bg="#FACD64", 
							width=size*11,height=self.h)
		self.canvas.bind("<Button-1>", self.click)
		self.canvas.place(x=0,y=0)
		
		self.board = board_obj(self.canvas,size)
		self.board.draw(self.game.board)
			
		self.data = Frame(self.tk, bg="#FACD64", width=size*4,height=self.h)
		self.data.place(x=size*11,y=0)
		self.log = Frame(self.data, bg="#FACD64", width=size*4,height=self.h*1//2)
		self.log.place(x=0,y=0)
		
		self.S = Scrollbar(self.log,width=size//6)
		self.T = Text(self.log, bg='white', font=('',14*size//150),height=15,width=27)
		self.T.config(state=DISABLED)
		self.S.pack(side=RIGHT, fill=Y)
		self.T.pack(side=LEFT, fill=Y)
		self.S.config(command=self.T.yview)
		self.T.config(yscrollcommand=self.S.set)
		
		self.button_before = Button(self.data,text="前一手", font=('',14*size//150),
									command=self.before)
		self.button_after  = Button(self.data,text="後一手", font=('',14*size//150),
									command=self.after)
		self.button_new    = Button(self.data,text="新一局", font=('',14*size//150),
									command=self.new_click)
		self.button_sur    = Button(self.data,text="投了", font=('',14*size//150),
									command=self.surrender)
		self.button_seminar= Button(self.data,text="研究會", font=('',14*size//150),
									command=self.start_seminar)
		self.button_save   = Button(self.data,text="儲存棋譜", font=('',14*size//150),
									command=self.save)
		
		self.button_before.place(x=0,y=size*5.55)
		self.button_after.place(x=size,y=size*5.55)
		self.button_new.place(x=size*2,y=size*5.55)
		self.button_sur.place(x=size*3,y=size*5.55)
		self.button_seminar.place(x=0,y=size*6.036)
		self.button_save.place(x=0,y=size*6.52)
		self.button_sur.config(state=DISABLED)
		
		self.move_list = Listbox(self.data,height=6,width=29,font=('',14*size//150))
		self.move_list.place(x=0,y=size*7)
	
	def save(self):
		now = self.first_his
		length = 1
		queue = [(now,1)]
		while queue:
			now,length = queue.pop(0)
			for i in now.child.values():
				queue.append((i,length+1))
			
		output = [[] for i in range(length)]
		output[0] = ['          ']
		now = self.first_his
		
		def dfs(now,moves,output):
			if moves>1:
				output[moves-1].append('{}'.format(get_str(now.move,10,True)))
			
			amount = 0
			if now.child:
				for record in now.child.values():
					if amount>0:
						output[moves-1].append('───┐　　　')
						for i in range(moves-1):
							output[i].append('　　　　　')
					
					dfs(record, moves+1, output)
					amount += 1
			else:
				for i in range(len(output)-moves):
					output[i+moves].append('　　　　　')
				
		dfs(now,1,output)
		for i in range(len(output)):
			if i:
				num = '第{:<3}手: '.format(i)
			else:
				num = '　    　'
			output[i] = num+'\t'.join(output[i]).replace('  ','　')
		
		output = '\n'.join(output)
		
		print(output)
		path = askF(filetypes=[('txt file','.txt')],title='儲存棋譜')
		print(path)
		
		with open(path,'w') as f:
			f.write(output)
	
	def turn_off(self):
		self.on = False
		if self.game_thread:
			self.game_thread.join()
		if self.semi_thread:
			self.semi_thread.join()
	
	def print_log(self, log:str, end='\n'):
		self.T.config(state=NORMAL)
		self.T.insert(END, log+end)
		self.T.see(END)
		self.T.see(END)
		self.T.config(state=DISABLED)

	def new_click(self):
		if self.game_thread:
			self.game_thread.join()
		self.button_new.config(state=DISABLED)
		self.game_thread = th.Thread(target=self.new_game)
		self.game_thread.start()
	
	def surrender(self):
		self.sur = True
	
	def move(self, move, now):
		move_str = self.game.print_step(move,self.pl,p=False)
		self.print_log('第{:2}手: {}'.format(len(self.last_his), move_str))
		
		self.game.move(move,self.pl)
		self.board.draw(self.game.board)
		
		new_record = record(copy(self.game),now)
		new_record.move = move_str
		self.last_his.expand(move_str,new_record)
		self.last_his = new_record
		
		end, winner = self.game.is_end()
		if end:
			self.state = 'pl'
			return winner
		
		self.pl = 1-self.pl
		now = 1-now
		self.state = self.player[now]
		self.temp = {}
	
	def new_game(self):
		self.game_lock = False
		self.game = Shogi(deepcopy(initial_board))
		self.temp = {}
		self.pl=0 if (self.player[0]=='pl' and self.player[1] !='pl') else 1
		now = 1
		
		self.state = self.player[now]
		self.last_his = record(self.game, 1-now)
		self.first_his = self.last_his
		
		self.button_new.config(state=DISABLED)
		self.button_before.config(state=DISABLED)
		self.button_after.config(state=DISABLED)
		self.button_seminar.config(state=DISABLED)
		self.button_sur.config(state=NORMAL)
		self.board.draw(self.game.board)
		
		self.print_log('新局開始\n先手為: {}'.format(pl_icon[self.pl]))
		while True and self.on:
			if self.sur:
				self.sur = False
				winner = -2
				break
			
			elif self.state.find('plmove')==0:
				move = self.temp[self.state.split(',')[1]]
				state = self.move(move,now)
				
				if state is not None:
					winner = state
					break
				now = 1-now
			
			elif self.state=='random':
				move = self.game.available(self.pl,all=False,random=True)
				state = self.move(move,now)
				
				if state is not None:
					winner = state
					break
				now = 1-now		
		
		if not self.on: return
		
		self.board.draw(self.game.board)
		state = self.end_play(winner)
		new_record = record(copy(self.game),now)
		new_record.move = pl_icon[now]+' '+state
		self.last_his.expand(pl_icon[now]+' '+state,new_record)
		
		self.button_new.config(state=NORMAL)
		self.button_seminar.config(state=NORMAL)
		self.button_sur.config(state=DISABLED)
	
	def end_play(self,winner):
		self.state = ''
		if winner==-2:
			winner = self.pl
			self.print_log('對局結束')
			state = '{}投了'.format('先手' if winner else '後手')
			self.print_log(state)
			return state
			
		elif winner==-1:
			if self.game.is_checkmate(1-self.pl):
				winner = self.pl
				self.print_log('對局結束')
				state = '{}勝'.format('先手' if winner else '後手')
				self.print_log(state)
				return state
			else:
				self.print_log('對局結束')
				self.print_log('千日手')
				return '千日手'
		else:
			self.print_log('對局結束')
			state = '{}勝'.format('先手' if winner else '後手')
			self.print_log(state)
			return state
	
	def start_seminar(self):
		if self.semi_thread:
			self.semi_thread.join()
		self.semi_thread = th.Thread(target=self.seminar)
		self.semi_thread.start()
		self.button_seminar.config(state=DISABLED)
	
	def seminar(self):
		if not self.last_his:
			self.last_his = record(self.game, 0)
			self.first_his = self.last_his
		self.pl = 1-self.last_his.pl
		
		self.state = 'pl'
		
		self.button_new.config(state=NORMAL)
		self.button_before.config(state=NORMAL)
		self.button_after.config(state=NORMAL)
		self.button_sur.config(state=DISABLED)
		
		self.game_lock = True
		while self.game_lock and self.on:
			if self.state.find('plmove')==0:
				move = self.temp[self.state.split(',')[1]]
				move_str = self.game.print_step(move,self.pl,p=False)
				
				self.game.move(move,self.pl)
				self.print_log('第{:2}手: {}'.format(len(self.last_his), move_str))
				self.board.draw(self.game.board)
				
				end, winner = self.game.is_end()
				if end:
					self.state = 'pl'
					state = self.end_play(winner)
					new_record = record(copy(self.game),self.pl)
					new_record.move = pl_icon[self.pl]+' '+state
					self.last_his.expand(state,new_record)
					self.last_his = new_record
				
				else:
					if move_str in self.last_his.child:
						self.last_his = self.last_his.child[move_str]
					else:
						new_record = record(copy(self.game),self.pl)
						new_record.move = move_str
						self.last_his.expand(move_str,new_record)
						self.last_his = new_record
				
				self.move_list.delete(0,END)
				self.move_list.insert(END,"下一手列表:")
				for i in self.last_his.child.keys():
					self.move_list.insert(END,i)
				
				self.pl = 1-self.pl
				self.temp = {}
				self.state='pl'
			sleep(0.001)	
			
		if not self.on:
			return		
		self.button_seminar.config(state=NORMAL)
	
	def after(self):
		if self.last_his.child:
			try:
				get = self.move_list.get(self.move_list.curselection())
			except:
				get = ''
			if get=="下一手列表:":
				self.pinrt_log("請選擇棋步")
			elif get=="":
				for i in self.last_his.child:
					get = i
			
			self.last_his = self.last_his.child[get]
			self.state = 'pl'
			
			self.print_log(f"前進至第{len(self.last_his)-1}手",end=':')
			self.print_log(self.last_his.move)
			
			self.move_list.delete(0,END)
			self.move_list.insert(END,"下一手列表:")
			for i in self.last_his.child.keys():
				self.move_list.insert(END,i)
			
			self.game = copy(self.last_his.board)
			self.pl = 1-self.last_his.pl
			self.board.draw(self.game.board)
			
	def before(self):
		if self.last_his.parent==None:
			self.print_log("已經回到最初局面了")
		else:
			self.last_his = self.last_his.parent
			self.state = 'pl'
			
			self.move_list.delete(0,END)
			self.move_list.insert(END,"下一手列表:")
			for i in self.last_his.child.keys():
				self.move_list.insert(END,i)
			
			self.print_log(f"退回至第{len(self.last_his)-1}手",end=':')
			self.print_log(self.last_his.move)
			self.game = copy(self.last_his.board)
			self.pl = 1-self.last_his.pl
			self.board.draw(self.game.board)
	
	def click(self,event):
		if self.unit*10>event.x>self.unit:
			x = event.y//self.unit+1
			y = event.x//self.unit-1
		elif event.x<self.unit:
			x = 0
			y = event.y//self.unit
		elif event.x>self.unit:
			x = 10
			y = 8-event.y//self.unit
		
		th.Thread(target=self.operate, args=(x,y)).start()
		
	def operate(self, x,y):
		if self.state=='pl':
			if 0<x<10:
				now = self.game.board[x][y]
				index = ((x-1)*9+y)*139
				
				if now and (now>0)==bool(self.pl):
					doable = []
					moves = self.game.available(self.pl)
					for i in moves:
						if index<=i<index+139:
							doable.append(i)
					
					for move in doable:
						pos, _move = divmod(move,139)
						i, j, _ = all_steps[_move]
						i = i if self.pl else -i
						self.temp[f'{x+i} {y+j}'+('成' if _move>65 else '')] = move
						self.board.highlight(x+i,y+j,'red')
					
					self.board.highlight(x,y,'aqua')
					self.state = 'pl_choose'
			else:
				own = 0 if self.pl==0 else 10
				if x!=own:return
				 
				now = self.game.board[own][y]
				if now:
					self.board.highlight(x,y,'aqua')
					doable = []
					moves = self.game.available(self.pl)
					for i in moves:
						if i%139==132+y:
							doable.append(i)
					
					for move in doable:
						pos, _move = divmod(move,139)
						x,y = divmod(pos,9)
						self.temp[f'{x+1} {y}打'] = move
						self.board.highlight(x+1,y,'red')

					self.state = 'pl_choose'
			
		elif self.state == 'pl_choose':
			if f'{x} {y}' in self.temp or f'{x} {y}成' in self.temp:
				up=f'{x} {y}成' in self.temp
				if up:
					if f'{x} {y}' in self.temp:
						up = tkinter.messagebox.askokcancel('升變', '要升變嗎?')
						self.state = 'plmove,'+f'{x} {y}'+('成' if up else '')
					else:
						self.state = 'plmove,'+f'{x} {y}成'
				else:
					self.state = 'plmove,'+f'{x} {y}'
				
			elif f'{x} {y}打' in self.temp:
				self.state = 'plmove,'+f'{x} {y}打'
			
			else:
				self.state = 'pl'
				self.board.draw(self.game.board)
	
	def main(self):
		self.on = True
		self.tk.mainloop()
		
if __name__ =='__main__':
	game = AoiShogi()
	game.main()
	game.turn_off()
