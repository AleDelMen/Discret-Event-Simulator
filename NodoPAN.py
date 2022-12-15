import random
import simpy
import time
from decimal import Decimal
import collections
from Pack import Pack
from Node import Node
from Canal import Canal
from printClass import printClass

class NodoPAN(Node):
	def __init__(self, env, idPAN, coordinator, name, grafo, printFunctions, probabilities, time):
		Node.__init__(self, env, idPAN, coordinator, name, probabilities, time) #The PAN Node inherits from the Node class
		self.commandCoor = [2, 3, 7] #Commands that a coordinator node can use
		self.commandNC = [1, 3, 4, 5, 6, 8, 9] #Commands that a device node can use
		self.grafo = grafo #Experimental graph
		self.nodes = [] #List of node objects
		self.printConsole = printFunctions[0] #Boolean variable to enable console printing
		self.printTxt = printFunctions [1] #Boolean variable to enable animation
		self.probabilities = probabilities #Probabilities list
		self.timeBetweenPack =time #Generate a packet approximately every x seconds

	def makeNetwork(self):
		self.canal = Canal(self.env, len(self.grafo))
		for i in self.grafo.keys():
			if i == self.name:
				continue
			elif len(self.grafo[i]) > 1:
				node = Node(self.env, self.idPAN, True, i, self.probabilities, self.timeBetweenPack)
				self.nodes.append(node)
			else:
				node = Node(self.env, self.idPAN, False, i, self.probabilities, self.timeBetweenPack)
				self.nodes.append(node)
		for i in self.nodes:
			auxVecinos = []
			if i.coordinator == True:
				for j in self.grafo[i.name]:
					auxVecinos.append(self.nodes[i.getAllindexOfNodes(self.nodes, j)[0]])
				printObject = printClass(self.printConsole, self.printTxt)
				yield self.env.process(i.setupNode(auxVecinos, self.commandCoor, self.canal, printObject))
			else:
				for j in self.grafo[i.name]:
					auxVecinos.append(self.nodes[i.getAllindexOfNodes(self.nodes, j)[0]])
				printObject = printClass(self.printConsole, self.printTxt)
				yield self.env.process(i.setupNode(auxVecinos, self.commandNC, self.canal, printObject)) 	