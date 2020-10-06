import threading as th
from time import time
from copy import copy,deepcopy

class record:
	__slots__ = ['board','pl','parent','child','steps','move']
	def __init__(self, board, pl):
		self.board = copy(board)
		self.pl = pl
		self.steps=1
		self.move=''
		self.parent = None
		self.child = {}
		
	def expand(self, move, next_record):
		next_record.parent = self
		next_record.steps = self.steps+1
		self.child[move] = next_record
	
	def __len__(self):
		return self.steps

class chess_obj:
	def __init__(self, canvas, size, y, x):
		self.chess = ('','步','香','桂','銀','金','角','飛','と','杏','圭','全','馬','龍','王','玉')
		self.canvas = canvas
		self.size = size
		self.hid = True
		
		self.x,self.y = x,y
		self.points_list = []
		self.num_list = tuple(['','']+[str(i) for i in range(2,19)])
		
		oX = size*(x+1.5)
		oY = size*(y-.93)+10
		self.points_list.append((	oX,oY,
									oX+size*0.32,oY+size*0.13,
									oX+size*0.4,oY+size*0.83,
									oX-size*0.4,oY+size*0.83,
									oX-size*0.32,oY+size*0.130))
		oY = size*(y)
		self.points_list.append((	oX,oY,
									oX+size*0.32,oY-size*0.13,
									oX+size*0.4,oY-size*0.83,
									oX-size*0.4,oY-size*0.83,
									oX-size*0.32,oY-size*0.13))
		oY = size*(y-.83)+10
		self.points_list.append((	oX,oY,
									oX+size*0.246,oY+size*0.1,
									oX+size*0.31,oY+size*0.64,
									oX-size*0.31,oY+size*0.64,
									oX-size*0.246,oY+size*0.1))
		oY = size*(y-.19)+10
		self.points_list.append((	oX,oY,
									oX+size*0.246,oY-size*0.1,
									oX+size*0.31,oY-size*0.64,
									oX-size*0.31,oY-size*0.64,
									oX-size*0.246,oY-size*0.1))
		self.points_list = tuple(self.points_list)
		
		self.text_back = self.canvas.create_rectangle(size*(x+1)+2, size*(y-1)+12,
									size*(x+2)-3, size*(y)+8, outline="")
		self.chess_image = self.canvas.create_polygon(self.points_list[0],outline="")
		self.num = self.canvas.create_text(size*(x+1.8),size*(y-.2)+10,)
		self.text = self.canvas.create_text(size*(x+1.5),size*(y-.5)+10,)
	
	def highlight(self,color):
		self.canvas.itemconfig(self.text_back, fill=color)
			
	def hidden(self):
		t,b,c,n = self.text, self.text_back, self.chess_image, self.num
		self.canvas.itemconfig(t, text='')
		self.canvas.itemconfig(b, fill='')
		self.canvas.itemconfig(c, fill="")
		self.canvas.itemconfig(n, text="")
		
	def display(self, now, amount=0):
		if now==14:
			now=15
		
		if now<0:
			a = 180
		else:
			a = 0
		
		if amount:
			n = self.num
			self.canvas.itemconfig(n, text=self.num_list[amount], font=('',10))
		
		chess = self.chess[abs(now)]
		t,b,c = self.text, self.text_back, self.chess_image
		self.canvas.itemconfig(b, fill='')
		
		color = '#E01600' if abs(now) in {8,9,10,11,12,13} else 'black'
		if abs(now) in {6,7,12,13,14,15}:
			self.canvas.itemconfig(t, text=chess, angle=a, 
								font=('',self.size*2//10),fill=color)
			self.canvas.coords(c, self.points_list[0 if now>0 else 1])
			self.canvas.itemconfig(c, fill='#E09E02')
		else:
			self.canvas.itemconfig(t, text=chess, angle=a, 
								font=('',self.size*2//13),fill=color)
			self.canvas.coords(c, self.points_list[2 if now>0 else 3])
			self.canvas.itemconfig(c, fill='#E09E02')

		
class board_obj:
	def __init__(self, canvas,size):
		self.canvas = canvas
		self.chess = ('','步','香','桂','銀','金','角','飛','と','杏','圭','全','馬','龍','王','玉')
		
		for i in range(10):
			now_x = size*(i+1)
			if i==0 or i==9:
				w = 10
			else:
				w = 4
			self.canvas.create_line(now_x, 10, now_x, size*9+10, width=w)
		
		for i in range(10):
			now_y = size*(i)+10
			if i==0 or i==9:
				w = 10
			else:
				w = 4
			self.canvas.create_line(size, now_y, size*10, now_y,width=w)
		
		self.board = [[None for i in range(9)] for i in range(11)]
		
		for i in range(1,10):
			for j in range(9):
				chess = chess_obj(self.canvas, size, i,j)
				self.board[i][j] = chess
		
		for i in range(7):
			chess = chess_obj(self.canvas, size, i+1,-1)
			self.board[0][i] = chess
		
		for i in range(7):
			chess = chess_obj(self.canvas, size, 9-i,9)
			self.board[-1][i] = chess

	def draw(self, gameboard):
		for i in range(1,10):
			for j in range(9):
				now = gameboard[i][j]
				chess_now = self.board[i][j]
				if now:
					th.Thread(target=chess_now.display,args=(now,)).start()
				else:
					th.Thread(target=chess_now.hidden).start()
		
		for i in range(7):
			num = gameboard[0][i]
			chess_now = self.board[0][i]
			if num:
				chess_now.display(-(i+1),num)
			else:
				chess_now.hidden()
		
		for i in range(7):
			num = gameboard[-1][i]
			chess_now = self.board[-1][i]
			if num:
				chess_now.display(i+1,num)
			else:
				chess_now.hidden()
	
	def highlight(self,x,y,color):
		self.board[x][y].highlight(color)
