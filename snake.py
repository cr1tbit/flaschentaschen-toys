#!/usr/bin/python3

ip = '10.14.10.25'
ip1 = '10.14.10.67'

import socket
import random
import time
from keyboard import _Getch
from threading import Timer

class Screen:
	def __init__(self, ip, port, x, y):
		self.screen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.ip = ip
		self.port = port
		self.screen_x = x
		self.screen_y = y
		
	def screen_matrix_to_bytes(self, data):
		result = bytearray()
		for y in range(self.screen_y):
			for x in range(self.screen_x):
				for color in range(3):
					result.append(data[x][y][color])
		return result
	
	def push(self, data):
		header = b"P6\n%d %d\n255\n" % (self.screen_x, self.screen_y)
		b = self.screen_matrix_to_bytes(data)
		self.screen.sendto(header + b, (self.ip, self.port))


class Canvas:
	def __init__(self, x,y):
		self.canvas_x = x
		self.canvas_y = y
		self.body = [[3*[0] for _ in range(y)]  for _ in range(x)]


	def point(self, xy,color=[255,255,255]):
		self.body[int(xy[0])][int(xy[1])] = color

	def line(self, a,b,color=[255,255,255]):
		self.point(a, color)
		self.point(b, color)
		x = a[0]
		y = a[1]
		if (a[0] < b[0]):
			xi = 1
			dx = b[0] - a[0]
		else:
			xi = -1
			dx = a[0] - b[0]

		if (a[1] < b[1]):
			yi = 1
			dy = b[1] - a[1]
		else:
			yi = -1
			dy = a[1] - b[1]
		
		if (dx > dy):
			ai = (dy - dx) * 2
			bi = dy * 2
			d = bi - dx
			while (x != b[0]):
				if (d >= 0):
					x += xi
					y += yi
					d += ai
				else:
					d += bi
					x += xi
				self.point([x,y], color)
		else:     
			ai = ( dx - dy ) * 2
			bi = dx * 2
			d = bi - dy
			while (y != b[1]):

				if (d >= 0):
					x += xi
					y += yi
					d += ai
				else:
					d += bi
					y += yi
				self.point([x, y], color)
		
	def square(self, a,b,color=[255,255,255]):
		for y in range(b[1] - a[1]):
			for x in range(b[0] - a[0]):
				self.body[a[0]+x+1][a[1]+y+1] = color

	def rainbow(self, stage):
		t = stage % 768
		if(stage < 256):
			color = [255-t,t,0]
			
		if(stage > 255 & stage < 512):
			t -= 256
			color = [0,255-t,t]

		if(stage > 511 & stage < 768):
			t -= 256
			color = [t,0,255-t] 

		return color

	def color(self, color):
		for y in range(self.canvas_y):
			for x in range(self.canvas_x):  
				self.body[x][y] = color

	def clear(self):
		self.color([0,0,0])

	def printMock(self):
		string = ''
		for y in range(self.canvas_y):
			for x in range(self.canvas_x):
				if(self.body[x][y] != [0,0,0]):
					string += '#'
				else:
					string += '_'
			string += '\n\r'
		return string


	def printScreen(self, size_x, size_y, offset_x=0, offset_y=0):
		returnBody = [[3*[0] for _ in range(size_y)]  for _ in range(size_x)]
		for y in range(size_y):
			for x in range(size_x):  
				returnBody[x][y] = self.body[offset_x + x][offset_y + y]
				
		return returnBody

	def print(self):
		return self.body


class Snake:
	length = 1
	map_width = 1
	map_height = 1
	direction = 'd'

	def __init__(self, map_width, map_height):
		self.body = [[0, 0] for _ in range(map_width * map_height)]
		self.map_width = map_width
		self.map_height = map_height
		self.body.insert(0, self.randomxy())
		self.food = self.randomxy()

	def randomxy(self):
		return [random.randint(0,self.map_width-1), random.randint(0,self.map_height-1)]

	def control(self, key):
		if(key == 'w' or key == 's' or key == 'a' or key == 'd'):
			self.direction = key

	def drawTo(self, canvas):
		if(self.direction == 'w'):
			self.body.insert(0, [self.body[0][0], (self.body[0][1]-1)%self.map_height])
		
		if(self.direction == 's'):
			self.body.insert(0, [self.body[0][0], (self.body[0][1]+1)%self.map_height])

		if(self.direction == 'a'):
			self.body.insert(0, [(self.body[0][0]-1)%self.map_width, self.body[0][1]])

		if(self.direction == 'd'):
			self.body.insert(0, [(self.body[0][0]+1)%self.map_width, self.body[0][1]])

		rainbowstate = 0
		canvas.clear()
		for i, pos in enumerate(self.body):

			if(self.food == self.body[0]):
				self.length += 1
				self.food = self.randomxy()

			if(i == self.length):
				break

			canvas.point(pos, canvas.rainbow(rainbowstate))
			rainbowstate += 32
			rainbowstate %= 768
			
			canvas.point(self.food)

			if(self.body[i][0] == self.body[0][0] and self.body[i][1] == self.body[0][1] and i!=0):
				self.length = 1
				canvas.color([255,0,0])
				break
		return canvas

class Game:
	gameloop = 0
	def __init__(self, ip, ip1, port, x, y):
		self.x = x
		self.y = y
		self.screen = Screen(ip, port, int(x/2), y)
		self.screen1 = Screen(ip1, port, int(x/2), y)
		self.canvas = Canvas(x, y)
		self.snake = Snake(x, y)
		

	def controller(self, key):
		self.snake.control(key)

	def loop(self):
		self.snake.drawTo(self.canvas) 

		print(self.canvas.printMock())
		self.screen.push(self.canvas.printScreen(int(self.x/2), self.y))
		self.screen1.push(self.canvas.printScreen(int(self.x/2), self.y, int(self.x/2)))
		self.gameloop = Timer(0.5, self.loop)
		self.gameloop.start()

	def stop(self):
		self.gameloop.cancel()



def main():
	getch = _Getch()

	game = Game(ip, ip1, 1337, 10, 8)

	game.loop()

	while True:
		
		if(getch() == "q"):
			break
		
		game.controller(getch())


	game.stop()

if __name__ == "__main__":
	main()

