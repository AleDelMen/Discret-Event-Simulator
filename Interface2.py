import networkx as nx
import matplotlib.pyplot as plt
from vpython import *
import numpy as np
import time

class Interface:
	def __init__(self, archivo, graph, nodePAN):
		self.Rsps = float(62500) #Modulation speed
		self.archivo = archivo #Pointer to a file
		self.nodePos = None #Nodes' coordinates
		self.graph = graph #Experimental graph
		self.nodes = {} #Sphere dictionary {identifier:sphere object}
		self.nodePAN = nodePAN #PAN node name
		self.events = [] #List of events to simulate
		self.tsym = 1/self.Rsps #Symbol time
		self.titleS = 'Slow Rate x' #Scroll title
		self.wts = [] #Scroll values list
		self.slider = None #Scroll object

	def getPosition(self):
		G = nx.Graph()
		G.add_nodes_from(self.graph.keys())

		for i in self.graph.keys():
			for j in self.graph[i]:
				G.add_edge(i, j)
		self.nodePos = nx.spring_layout(G)

	def nodeCreation(self):
		for i in self.graph.keys():
			if self.nodePAN == i :
				self.nodes[i] = sphere(pos=vector(self.nodePos[i][0], self.nodePos[i][1], 0),radius=0.1, color=color.red)
			elif len(self.graph[i]) == 1 :
				self.nodes[i] = sphere(pos=vector(self.nodePos[i][0], self.nodePos[i][1], 0),radius=0.1, color=color.white)
			else:
				self.nodes[i] = sphere(pos=vector(self.nodePos[i][0], self.nodePos[i][1], 0),radius=0.1, color=color.yellow)
			label(pos=self.nodes[i].pos, text=i, height=20, font='sans', opacity = 0, box = False, color = color.black)

	def edgeCreation(self):
		for i in self.graph.keys():
			for j in self.graph[i]:
				cylinder(pos = self.nodes[i].pos, axis = self.nodes[j].pos - self.nodes[i].pos, radius = 0.01, color = color.white)

	def packCreation(self, typeF, source, destination):
		a = self.nodes[source].pos
		b = self.nodes[destination].pos - self.nodes[source].pos
		if typeF == 'DAT':
			return sphere(pos = a, axis = b, radius=0.03, color=color.cyan)
		elif typeF == 'COM':
			return sphere(pos = a, axis = b, radius=0.03, color=color.blue)
		else:
			return sphere(pos = a, axis = b, radius=0.03, color=color.green)

	def getEvent(self):
		i = 0
		for line in self.archivo:
			event = []
			data = line.split()
			if data[0] != 't' or data[7] == 'Termina':
				continue
			else:
				package = self.packCreation(data[3], data[1], data[2])
				event.append(package)
				event.append(float(data[6])*2*self.tsym)
				event.append(float(data[8]))
				event.append(i)
				event.append(event[0].axis + event[0].pos)
				self.events.append(event)
				i += 1
				f = open ('Evento.txt', 'a')
				f.write("".join(data))
				f.write("\n")
				f.close()
		self.archivo.close()
		#Creating a placebo event for the simulation to run correctly
		event = []
		package = sphere(pos = vector(0,0,0), radius=0.03, visible = False)
		event.append(package)
		event.append(1*2*self.tsym)
		event.append(float(data[8]) + 1)
		event.append(i)
		event.append(vector(1,1,1))
		self.events.append(event)

	def set_background(self, sl):
		self.wts[0].text = '{}'.format(sl.value)


	def start(self):
		startTime = time.time()
		events = []
		event = self.events.pop(0)
		flagStart = []
		flagStop = []
		initialPos = []
		flagSim = True
		while flagSim:
			t =time.time()
			rate((4*self.Rsps/self.s.value))
			currentTime = time.time()
			while True:
				if currentTime - startTime >= (event[2] * self.s.value):
					events.insert(0, event)
					flagStart.append(True)
					flagStop.append(False)
					initialPos.append(vector(event[0].pos))
					if self.events:
						event = self.events.pop(0)
					else:
						break
				else:
					break
			for i in events:
				if flagStart[i[3]] == True and flagStop[i[3]] == False:
					if time.time() - startTime >= (i[1]+i[2])*self.s.value:
						i[0].visible = False
						events.remove(i)
						flagStop[i[3]] = True
						if len(events) == 0:
							flagStart.clear()
							flagStop.clear()
							self.eventsSim.clear()
							if len(self.events) == 0:
								flagSim = False
					else:
						i[0].pos = initialPos[i[3]] +  ((((time.time() - startTime) - (i[2]*self.s.value))/((i[1])*self.s.value)) * i[0].axis)


	def setUp(self):
		self.getPosition()
		self.nodeCreation()
		self.edgeCreation()
		self.getEvent()
		self.s = slider(length=300, left=10, min=100, max=12000, step=100, bind = self.set_background)
		scene.append_to_caption('    '+self.titleS+' ')
		self.wts.append(wtext(text='0.000'))
		scene.append_to_caption('\n\n')
		self.s.value = 4000
		self.wts[0].text = '4000'
		self.start()

def main():
	#First test
	#graph = {'A':['B'], 'B':['A']}
	#Second test
	#graph = {'A':['B', 'C', 'D', 'E', 'F', 'G'], 'B':['A'], 'C':['A'], 'D':['A'], 'E':['A'], 'F':['A'], 'G':['A']}
	#Third test
	graph = {'A':['B', 'C', 'D', 'E'], 'B':['A'], 'C':['A', 'I', 'H'], 'D':['A', 'L', 'K', 'J'], 
		 'E':['F', 'G', 'A'], 'F':['E'], 'G':['E'], 'H':['C'], 'I':[ 'C'], 'J':['D'], 'K':['D'], 
		 'L':['D']}
	f = open ('Registro.txt', 'r')
	nodePANName = 'A'


	scene.width = 1200
	scene.height = 720
	title = 'IEEE 802.15.4 MAC Simulator\n'
	scene.title = title
	I = Interface(f, graph, nodePANName)
	I.setUp()


if __name__ == '__main__':
    main()