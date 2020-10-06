from copy import copy,deepcopy
from time import time,sleep
from random import choice,shuffle,randint
from tkinter import *
import sys



def get_str(s, limit=6, back=False):
	'''
	自製format用來限制長度並判斷全半形
	'''
	s = str(s)
	res = ''
	amount = 0
	for i in s:
		ch = ord(i)
		amount += 1 if ch<12288 else 2
		if amount>limit:
			amount -= 1 if ord(i)<12288 else 2
			break
		res += i
	
	if back:
		return res + ' '*(limit-amount)
	else:
		return ' '*(limit-amount) + res

initial_board = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
				[ -2, -3, -4, -5,-14, -5, -4, -3, -2],
				[  0, -7,  0,  0,  0,  0,  0, -6,  0],
				[ -1, -1, -1, -1, -1, -1, -1, -1, -1],
				[  0,  0,  0,  0,  0,  0,  0,  0,  0],
				[  0,  0,  0,  0,  0,  0,  0,  0,  0],
				[  0,  0,  0,  0,  0,  0,  0,  0,  0],
				[  1,  1,  1,  1,  1,  1,  1,  1,  1],
				[  0,  6,  0,  0,  0,  0,  0,  7,  0],
				[  2,  3,  4,  5, 14,  5,  4,  3,  2],
						[0, 0, 0, 0, 0, 0, 0, 0, 0]]

F = False
T = True
nums = ('','一','二','三','四','五','六','七','八','九')
cnums = {i:j for i,j in zip(nums,range(10))}
position = tuple((i,j) for i in range(1,10) for j in range(9))

s = range(1,9)
all_steps = [(-i, 0, F) for i in s]+\
			[( 0, i, F) for i in s]+\
			[( i, 0, F) for i in s]+\
			[( 0,-i, F) for i in s]+\
			[(-i,-i, F) for i in s]+\
			[(-i, i, F) for i in s]+\
			[( i, i, F) for i in s]+\
			[( i,-i, F) for i in s]

all_steps += [(-2,1,F),(-2,-1,F)]
all_steps += [(i[0],i[1],T) for i in all_steps]
all_steps = tuple(all_steps)

routes = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
routes[1] = (0,)
routes[2] = (7,)
routes[3] = (64,65)
routes[4] = (0,32,40,48,56)
routes[5] = (0,8,16,24,32,40)
routes[6] = (39,47,55,63)
routes[7] = (7,15,23,31)
routes[8] = routes[9] = routes[10] = routes[11] = (0,8,16,24,32,40)
routes[12] = (0,8,16,24,39,47,55,63)
routes[13] = (32,40,48,56,7,15,23,31)
routes[14] = (0,8,16,24,32,40,48,56)
routes = tuple(routes)

chesses = ('','步','香','桂','銀','金','角','飛','成步','成香','成桂','成銀','馬','龍','王')
up_map = (0,8,9,10,11,0,12,13,1,2,3,4,6,7)
chess_map = {}
for i in range(15):
	chess_map[chesses[i]] = i

pl_icon = ('☖','☗')
value_table = [0,1,3,5,8,9,14,15,7,7,7,7,18,20,0]

class Shogi:
	def __init__(self, board=deepcopy(initial_board)):
		self.board = board
		self.his = {}
	
	def __copy__(self):
		return Shogi(deepcopy(self.board))
	
	#印出盤面 
	#Linux跟Windows的terminal的格式不同 
	#linux要將get_str函數的ord(s)<改成10000 windows要9000
	def __str__(self):
		a,b,c,d,e,f,g,h,i = self.board[0]
		out = '┌──────'+'┬──────'*8+'┐'
		spliter = '\n├──────'+'┼──────'*8+'┤'
		
		out += '\n│      │      │ 步:{:2}│ 香:{:2}│ 桂:{:2}│ 銀:{:2}│ 金:{:2}│ 角:{:2}│ 飛:{:2}│'\
				.format(a,b,c,d,e,f,g)
		out += spliter*2+'\n│'
		
		for i in self.board[1:10]:
			for j in range(9):
				if i[j]>0:
					now = get_str('△'+chesses[abs(i[j])])
				elif i[j]<0:
					now = get_str('▽'+chesses[abs(i[j])])
				else:
					now = '      '
				out += '{}│'.format(now)
			out += spliter+'\n│'
		out = out[:-2]
		
		a,b,c,d,e,f,g,h,i = self.board[-1]
		out += spliter
		out += '\n│ 步:{:2}│ 香:{:2}│ 桂:{:2}│ 銀:{:2}│ 金:{:2}│ 角:{:2}│ 飛:{:2}│      │      │'\
				.format(a,b,c,d,e,f,g)
		out += '\n└──────'+'┴──────'*8+'┘'
		return out
	
	def get_move_by_str(self, string, pl):
		if string=="投了":
			return "NO Move"
		
		moves = self.available(pl)
		if not moves:
			return "NO Move"
		moves_str = {(self.print_step(i,pl,p=False)[1:]):i for i in moves}
		
		if string in moves_str:
			move = moves_str[string]
			return move
		else:
			return None
	
	#移動
	def move(self,s, pl):
		pos,move = s//139, s%139
		x,y = pos//9+1, pos%9
		self_c = -1 if pl else 0
		
		if move>131:			#打入
			chess = move-131
			self.board[self_c][chess-1]-=1
			self.board[x][y] = chess*(1 if pl else -1)
		else:					#一般操作
			m = all_steps[move]
			r, c, up = m
			if not pl:r = -r
							
			nx,ny = x+r, y+c
			origin = self.board[x][y]
			on = abs(self.board[nx][ny])
			self.board[x][y], self.board[nx][ny] = 0, origin
			
			if on and on!=14:
				if on<8:
					self.board[self_c][on-1] += 1
				else:
					self.board[self_c][up_map[on]-1] += 1
			
			if up:
				self.board[nx][ny] = up_map[abs(origin)]
				if not pl:
					self.board[nx][ny] *= -1
		
		#儲存出現次數
		self.his[str(self.board)] = self.his.get(str(self.board),0)+1
	
	def available(self,player,all=True,random=False,ai=False):
		doable = []						#可行棋步
		self_c = -1 if player else 0	#持駒所在行數
		own = self.board[self_c]		#持駒
		
		for i,j in position:			#遍歷棋盤
			now = self.board[i][j]		#現在的棋子
			n = abs(now)				#(正為先手負為後手)
			now_pos = ((i-1)*9+j)*139	#可行棋步為一維array除存 故計算出這個位置的棋步起始位置
			
			if now==0:					#打入
				#步/香（不能打在最後一排)
				if (i>1 and player) or (i<9 and not player):
					if own[0]>0:		
						pawn2 = False	#二步偵測
						for r in range(1,10):
							if r==i:continue
							k = self.board[r][j]
							if abs(k)==1 and (k>0)==player:
								pawn2 = True
								break
								
						if not pawn2:	#打步詰偵測(前方是否為王將 是的話有沒有造成將死)
							if self.board[i+(-1 if player else 1)][j]==(-14 if player else 14): 
								temp = copy(self)
								temp.move(now_pos+132, player)
								if temp.available(not player,all=False)!=None:
									doable.append(now_pos+132)
							else:
								doable.append(now_pos+132)
					
					if own[1]>0:		#打入香車
						doable.append(now_pos+132+1)
				
				#桂（不能打在最後兩排)
				if own[2]>0:
					if (i>2 and player) or (i<8 and not player):
						doable.append(now_pos+132+2)
				
				#金銀飛角
				for i in range(3,7):
					if own[i]>0:
						doable.append(now_pos+132+i)
			
			#自己的棋
			elif (now>0)==player:
				avai = routes[n]				#這個棋的可行走法
				
				for s in avai:					#遍歷可行走法並判斷合法與否
					x, y, _ = all_steps[s]		#讀取走法的x變化及y變化
					x *= (1 if player else -1)	#如果是後手要上下顛倒
					
					if s%8==0 or s==65:			#步桂銀金王
						now_x, now_y = x+i, y+j
						next = now_x+x
						
						#超過範圍
						if not (1<=now_x<=9 and 0<=now_y<=8):
							continue

						#偵測目標位置是否已經有棋 如果有則判斷是否為敵方
						on = self.board[now_x][now_y]
						if not on or (on>0)!=player:
							#強制升變
							if n<4 and (1>next or next>9):
								doable.append(now_pos+s+66)
								continue
							
							#升變判斷（ai模式開的時候 步皆強制升變)
							if player:
								if (now_x<4 or (i<4 and now_x>3)) and n<8 and n!=5:
									doable.append(now_pos+s+66)
									if ai and abs(now)==1:continue
							else:
								if (now_x>6 or (i>6 and now_x<7)) and n<8 and n!=5:
									doable.append(now_pos+s+66)
									if ai and abs(now)==1:continue
							doable.append(now_pos+s)

					else:					#香角飛龍馬
						#方向
						x_d = y_d = 0
						if x: 
							x_d = 1 if x>0 else -1
						if y: 
							y_d = 1 if y>0 else -1
						
						#從動一格開始找
						step = s-8
						now_x,now_y = i,j
						for k in range(1,9):
							step += 1
							now_x += x_d; now_y += y_d
							
							#超出範圍
							if not (0<now_x<10 and -1<now_y<9):
								break
							else:
								on = self.board[now_x][now_y]
							
								if not on or (on>0)!=player:
									next = now_x + x_d
									#香的強制升變判斷
									if n==2 and (next>9 or next<1):
										doable.append(now_pos+step+66)
										break
									
									#同 步桂銀金王
									if player:
										if (now_x<4 or (i<4 and now_x>3)) and n<8:
											doable.append(now_pos+step+66)
									else:
										if (now_x>6 or (i>6 and now_x<7)) and n<8:
											doable.append(now_pos+step+66)
										
									doable.append(now_pos+step)
									#如果遇到有棋的位置就停下來
									if on:break
								else:
									break
		#過濾自殺棋步
		if random:
			shuffle(doable)
		
		chosen = []						#expand的所有子節點(概念上)
		while True:						#過濾自殺棋步
			move = None
			while doable:
				move = doable.pop()
				temp = copy(self)
				temp.move(move,player)
				
				if temp.is_checkmate(not player)==False:
					break
				else:
					move = None
			
			if move==None:
				break
			else:
				if all:
					chosen.append(move)
				else:
					return move
		if all:
			return chosen
		else:
			return None
	
	#利用available的算法偵測有沒有on包含14(王)
	def is_checkmate(self,pl):
		checkmate = False
		
		for i,j in position:
			now = self.board[i][j]
			if now and (now>0)==pl:
				avai = routes[abs(now)]
				
				for s in avai:
					x, y, _ = all_steps[s]
					x = x if pl else -x
					
					if s%8==0 or s==65:	#步銀金王
						now_x, now_y = i+x, j+y
						if now_x<1 or now_x>9 or now_y<0 or now_y>8:
							continue
						on = self.board[now_x][now_y]
						if abs(on)==14 and (on>0)!=pl:
							return True
					
					else:#香角飛龍馬
						#方向
						x_d = y_d = 0
						if x: x_d = 1 if x>0 else -1
						if y: y_d = 1 if y>0 else -1
						
						#從動一格開始找
						for k in range(1,9):
							now_x, now_y = k*x_d+i, k*y_d+j
							
							if now_x<1 or now_x>9 or now_y<0 or now_y>8:
								break
							else:
								on = self.board[now_x][now_y]
							
								if abs(on)==14 and (on>0)!=pl:
									return True
								elif on:
									break
		return False
	
	def is_end(self):
		first = self.available(1, all=False)	#先手無路可走:後手勝
		if first==None:
			return True,0
		
		second = self.available(0, all=False)	#後手無路可走:先手勝
		if second==None:
			return True,1
		
		board = str(self.board)					#同一盤面出現四次:千日手
		if board in self.his and self.his[board]>=4:
			if self.is_checkmate(1):			#先手連續王手的千日手 後手勝
				return True,0
			elif self.is_checkmate(0):			#後手連續王手的千日手 先手勝
				return True,1
			else:
				return True,-1
		
		return False,-1

	#利用available的算法偵測有沒有其他可以到達目標位置的棋步
	#用來判斷棋譜的左右上直寄引
	def is_same(self,pl,pos,chess):
		same = []
		avai = routes[abs(chess)]
		
		for i,j in position:
			now = self.board[i][j]
			if now==chess:
				for s in avai:
					x, y, _ = all_steps[s]
					x = x if pl else -x
					
					if s%8==0 or s==65:	#步銀金王
						now_x, now_y = i+x, j+y
						if (now_x,now_y)==pos:
							same.append((j+1,i))
					
					else:#香角飛龍馬
						#方向
						x_d = y_d = 0
						if x: x_d = 1 if x>0 else -1
						if y: y_d = 1 if y>0 else -1
						
						#從動一格開始找
						for k in range(1,9):
							now_x, now_y = k*x_d+i, k*y_d+j
							
							if now_x<1 or now_x>9 or now_y<0 or now_y>8:
								break
							else:
								on = self.board[now_x][now_y]

								if (now_x,now_y)==pos:
									same.append((j+1,i))
								if on:
									break
		return same
		
	#印出棋步
	@staticmethod	
	def get_info(pl,target, move, other):
		info_list = {i:[] for i in "左右上寄直引"}
		x,y = target
		m_x,m_y = move
		d_x,d_y = m_x<x,m_y<y
		
		if m_x==x:			#原位置與目標位置在同一行上
			if d_y == pl:	#後退
				return '引'
			else:
				return '直'	#前進
		
		elif m_y==y:		#原位置與目標位置在同一列上
			horizon = True	#檢查有沒有其他同列棋
			for i in other:
				if i[1]==y:
					horizon = False
					break
			
			if horizon:		#如果沒有同列棋 輸出寄
				return '寄'
			else:			#若有 檢查左右
				return '右' if d_x==pl else '左'
		
		else:
			if d_y!=pl:
				vert_only = True#檢查是否只有自己在下側
				for i in other:
					if (i[1]<y) == d_y:
						vert_only = False
						break
				if vert_only:
					return '上'
				
			side_only = True#檢查是否為這側唯一(左右)
			for i in other:
				if (i[0]<x) == d_x:
					side_only=False
					break
			
			if side_only:	#如果是 直接輸出左右
				return '右' if d_x==pl else '左'
			else:			#不是本側
				if y==m_y:
					return '右寄' if d_x==pl else '左寄'
				elif d_x==pl:
					return '右引' if d_y==pl else '右上'
				elif d_x!=pl:
					return '左引' if d_y==pl else '左上'
	
	def print_step(self,s,first,end='\n',p=True):
		pos,move = divmod(s,139)
		x,y = divmod(pos,9)
		
		da = move>131
		if da:
			chess = chesses[move-131]
			out = '{}{}{}{}打'.format(pl_icon[first], 9-y, nums[x+1], chess)
		else:
			m = all_steps[move]
			if not first:
				m = (-m[0],m[1],m[2])
			c = m[2]
			
			chess = chesses[abs(self.board[x+1][y])]
			pos = (9-(y+m[1]),x+m[0]+1)
			
			info = ''
			same = self.is_same(first, (pos[1],y+m[1]), self.board[x+1][y])
			if len(same)>1:
				same.remove((y+1,x+1))
				info = self.get_info(first,(pos[0],pos[1]),(9-y,x+1),same)
			
			x,y = pos[0], nums[pos[1]]
			out ='{}{}{}{}{}{}'.format(pl_icon[first], x, y, chess, info, '成'if c else '')
		
		if p:
			print(out, end=end)
		return out

class State:
	def __init__(self, board, pl):
		self.pl = pl
		self.Board = copy(board)
	
	def __str__(self):
		return self.Board.__str__()
	
	def __eq__(self,other):
		return self.pl==other.pl and self.Board.board==other.Board.board
	
	def situation(self):
		actions = self.Board.available(self.pl)
		if not actions:
			return True, 1-self.pl, []
		else:
			return False, None, actions
	
	def get_next(self,move):
		temp = copy(self.Board)
		temp.move(move,self.pl)
		new = State(temp, 1-self.pl)
		
		return new
	
	def draw(self):
		return False
	
	def __copy__(self):
		return State(copy(self.Board), self.pl)

def random_play():	
	a = Shogi()
	player = 1
	his = 0
	
	T0 = time()
	while True:
		move = a.available(player, False, True)
		if move==None:
			break
		
		print('\n第{:2}手: '.format(his+1), end='')
		a.print_step(move,player)
		a.move(move, player)
		print(a)
		
		his += 1
		player = not player
	
	T1 = time()
	print('Total Move: {}'.format(his))
	print('Total Cost: {}s'.format(str(T1-T0)[:5]))
	print('Each Cost : {}us'.format(str((T1-T0)/his*1000000)[:5]))
	print('Winner    : {}'.format('先手' if not player else '後手'))
	

if __name__ =='__main__':
	Shogi().print_step(10425+40,1)
