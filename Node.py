import random
import simpy
import time
from decimal import Decimal
import collections
from Pack import Pack
from printClass import printClass
from Canal import Canal

#Parametros establecidos en 802.15.4

class Node:

	def __init__(self, env, idPAN, coordinator, name, probabilities, time):
		self.Rsps = float(62500) #Modulation speed
		self.sym = 4 #A symbol has 4 bits
		self.Rbps = self.Rsps * self.sym ##Transmission speed
		self.tsym = 1/self.Rsps #Symbol time
		self.timeMaxToSleep = time #Generate a packet approximately every x seconds
		self.name = name #Node identifier
		self.env = env  #The simulation environment
		self.canal =None #transmission medium
		self.idPAN = idPAN #Identifier of the source network
		self.coordinator = coordinator #Boolean variable to know if a node is coordinator
		self.EBTime = 0 #Exponential Backoff time
		self.macMinBE = 3 #EB minimum value
		self.macMaxBE = 5	#EB maximum value
		self.BEexp = self.macMinBE #Exponential Backoff
		self.unitEBPeriod = 20*self.tsym #Exponential backoff period time
		self.macMaxCSMAEB =  4 #Maximum attempts to transmit a packet, after the value of macMaxBE
		self.auxBEexp = 0 #Auxiliary variable to count the number of repetitions of macMaxBE
		self.paqTirados = 0 #Number of packages discarded
		self.paqsent = 0 #Number of packages sent
		self.paqReceived = [] #List of received packages
		self.ACKReceived = None #Auxiliary variable to store an ACK
		self.paqReceivedCorrectly = 0 #Number of packages received correctly
		self.vecinos = None #Node neighbor list
		self.queue = []#List of created packages
		self.aTurnaroundTime = 12 * self.tsym #Time a node waits to send an ACK
		self.timeToWaitAnACK = 54 * self.tsym #Time a node waits to receive an ACK
		self.pack = None #Auxiliary variable to store the packet to be transmitted
		self.packAppend = None #Auxiliary variable to store the created package
		self.command = None #Command list
		self.txProcess = None #Auxiliary variable where the transmission process is stored
		self.aMinSIFSPeriod = 12*self.tsym #Time between short frames
		self.aMaxSIFSFrameSize = 18 #Maximum number of bytes in a short frame
		self.aMinLIFSPeriod = 40*self.tsym #Time between long frames
		self.CCAtime = 8*self.tsym #CCA time
		self.probTC = probabilities[0] #Probability of creating a command package every time a data package is created
		self.flagRx = False #Reception flag
		self.flagTx = False #Transmission flag
		self.packACK = None #Auxiliary variable to generate ACK packages
		self.packACKTx = None #Auxiliary variable to store the ACK packets to be transmitted
		self.rxProcess = None #Auxiliary variable where the reception process is stored
		self.packRx = {} #Dictionary of packages received at the same time
		self.flagTO = False #Flag indicating a collision
		self.flagIFS = False #Flag indicating whether the IFS timeout has occurred
		self.error = 0.000001 #Error constant
		self.printObject = None #Flag to enable or disable console printing
		self.probError = probabilities[1] #Probability that a package contains errors, without considering collisions
		self.ACKrequestProcess = None #Auxiliary variable where the ACK reception process is stored
		self.flagBE = False #Flag to drop a packet that reached macMaxCSMAEB
		self.txProcessACK = None #Auxiliary variable where the ACK transmission process is stored
		self.EBprocess = None #Auxiliary variable where the Exponential Bacoff process is stored
		self.IFSprocess = None #Auxiliary variable where the IFS process is stored
		self.flagACKTx = False #Flag to indicate an ACK was transmitted
		self.flagACKRx = False #Flag to indicate an ACK was received
		self.flagRxComplete = False #Flag to indicate that a package was received
		self.processAuxACKRx = None #Auxiliary variable where the auxiliary process of receiving an ACK is stored
		self.probACK = probabilities[2] #Probability that a package requires ACK

	def get_index(self, probability):
		c_probability = 0
		sum_probability = []
		for p in probability:
			c_probability += p
			sum_probability.append(c_probability)
		r = random.random()
		for index, sp in enumerate(sum_probability):
			if r <= sp:
				return index
			return len(probability)-1

	def probability(self, P):
		response = [True, False]
		probability = [P, 1-P]
		resp_index = self.get_index(probability)
		return response[resp_index]

	def exponentialBackOff(self):
		if self.BEexp < self.macMaxBE + 1:
			return random.randint(0, pow(2, self.BEexp))
		else:
			self.auxBEexp += 1
			if self.auxBEexp >= self.macMaxCSMAEB + 1:
				self.paqTirados += 1
				self.BEexp = self.macMinBE 
				self.auxBEexp = 0
				self.flagBE = True
				return random.randint(0, pow(2, self.BEexp))
			return random.randint(0, pow(2, self.macMaxBE))

	def getEB (self):
		self.EBTime = self.exponentialBackOff() * self.unitEBPeriod

	def unsuccessfulTx (self, pack):
		self.BEexp += 1
		self.getEB()
		if self.auxBEexp <= self.macMaxCSMAEB + 1 and pack.auxFrameRetries < pack.aMaxFrameRetries +1 and self.flagBE == False:
			self.queue.insert(0, pack)
		else:
			self.printObject.printTx(pack, self.env.now, 'Se tira', self.paqsent, self.paqTirados, '10', '5')
			self.printObject.printTxt(pack, self.env.now, 'dt', pack.node.name, pack.source, pack.totalLen, '-', '-', self.pack.auxFrameRetries)
			self.successfulTx()
			self.flagBE = False

	def successfulTx(self):
		self.auxBEexp = 0
		self.BEexp = self.macMinBE
		self.getEB()

	def makePack (self, typeF, secuence):
		node = random.choice(self.vecinos)
		typeF = typeF
		self.packAppend = Pack(typeF, secuence, node, self.name, self.idPAN)
		self.packAppend.ACKrequest = self.probability(self.probACK)
		self.packAppend.setupFrame(0, self.command)
		self.printObject.printPack(self.packAppend, self.env.now)
		self.printObject.printTxt(self.packAppend, self.env.now, 'c', self.packAppend.node.name, self.packAppend.source, self.packAppend.totalLen, '-', '-', '-')
		self.queue.append(self.packAppend)

	def putQueue (self):
		yield self.env.timeout(self.tsym/self.sym)
		secuence = 0
		while True:
			self.makePack ("DAT", secuence)
			secuence += 1
			if self.probability(self.probTC):
				self.makePack ("COM", secuence)
				secuence += 1
			yield self.env.timeout(random.expovariate(1.0/self.timeMaxToSleep))

	def getAllindexOfPacks(self, list, nameDest):
		return filter(lambda a: list[a].node.name == nameDest, range(0,len(list)))

	def getAllindexOfPacksRx(self, list):
		return filter(lambda a: list[a] == True, range(0,len(list)))

	def getAllindexOfNodes(self, list, source):
		return filter(lambda a: list[a].name == source, range(0,len(list)))

	def ackTx(self, pack, time):
		try:
			typeF = "ACK"
			nodeIndex = self.getAllindexOfNodes(self.vecinos, pack.source)
			node = self.vecinos[nodeIndex[0]]
			self.packACK = Pack(typeF, pack.secuence, node, self.name, self.idPAN)
			self.packACK.ACKtime = time
			timeAux = self.env.now - self.packACK.ACKtime
			if timeAux <= self.unitEBPeriod:
				if  timeAux <= self.aTurnaroundTime:
					self.printObject.printTxACK(self.packACK, self.env.now, 'Esperando tiempo de ACK', 'No ha caducado', self.paqsent, self.paqTirados, timeAux)
					yield self.env.timeout(self.aTurnaroundTime - timeAux - self.error)
				if self.flagTx == True or self.flagRx == True:
					yield self.env.timeout(self.error)
					while True:
						if self.flagTx == True or self.flagRx == True:
							yield self.env.timeout(self.tsym/self.sym)
						else:
							timeAux = self.env.now - self.packACK.ACKtime
							if timeAux > self.unitEBPeriod:
								self.printObject.printTxACK(self.pack, self.env.now - self.error, '---', 'Ha caducado', self.paqsent, self.paqTirados, '---')							
							else:
								self.packACK.setupFrame(self.env.now, self.command)
								self.queue.insert(0, self.packACK)
								self.pack = self.queue.pop(0)
								self.txProcess = self.env.process(self.tx())
							self.flagACKTx = False
							self.txProcessACK = None
							break
				else:
					self.flagACKTx = False
					self.txProcessACK = None
					self.packACK.setupFrame(self.env.now + self.error, self.command)
					self.queue.insert(0, self.packACK)
					self.pack = self.queue.pop(0)
					self.txProcess = self.env.process(self.tx())
			else:
				self.printObject.printTxACK(self.pack, self.env.now, '---', 'Ha caducado', self.paqsent, self.paqTirados, '---')
				self.flagACKTx = False
				self.txProcessACK = None
		except simpy.Interrupt as i:
			self.printObject.printTxACK(self.pack, self.env.now, '---', 'Ha caducado', self.paqsent, self.paqTirados, '---')
			self.flagACKTx = False
			self.txProcessACK = None

	def FCScalculate(self, pack):
		if self.probability(self.probError):
			pack.FCSbool = True
		else:
			pack.FCSbool = False

	def rx(self):
		while True:
			if self.flagTx == True:
				yield self.env.timeout(self.tsym/self.sym)
				continue
			else:
				packSource = self.getAllindexOfPacks(self.canal.packT, self.name)
				if packSource:
					for j in range(0,len(packSource)):
						i = packSource[0]
						pack = self.canal.packT.pop(i)
						if pack.txTime + (self.tsym/self.sym) + self.error > self.env.now:
							self.packRx[pack] = 0
							lista = [o.source for o in self.packRx.keys()]
							if pack.typeF == 'ACK':
								self.printObject.printRxACK(pack, self.env.now, 'Comienza', pack.source, pack.node.name, '---')
								self.printObject.printTxt(pack, self.env.now, 'r', pack.node.name, pack.source, pack.totalLen, 'Comienza', pack.FCSbool, '-')
							else:
								self.printObject.printRx(pack, self.env.now, lista, 'Comienza', '---', 'None')
								self.printObject.printTxt(pack, self.env.now, 'r', pack.node.name, pack.source, pack.totalLen, 'Comienza', pack.FCSbool, '-')
							if self.flagRx == True or len(packSource) > 1 or self.flagTO == True:
								self.printObject.printCol(pack.source, self.env.now, self.name)
								self.flagTO = True
							packSource = self.getAllindexOfPacks(self.canal.packT, self.name)
							self.flagRx = True
						else:
							continue
				if len(self.packRx) != 0:
					if self.flagRxComplete:
						self.flagRxComplete = False
					else:
						yield self.env.timeout(self.tsym/self.sym)
					self.packRx = {key: self.packRx[key] + self.tsym/self.sym for key in self.packRx}
					fullyRxPack = {key: self.packRx[key] + self.error >= (key.totalLen*2*self.tsym  - self.tsym/self.sym) for key in self.packRx}
					indexOffullyRxPack = self.getAllindexOfPacksRx(fullyRxPack.values())
					if indexOffullyRxPack :
						self.flagRxComplete = True
						yield self.env.timeout(self.tsym/self.sym - self.error)
						for i in indexOffullyRxPack:
							if self.flagTO == False and fullyRxPack.keys()[i].FCSbool == None:
								self.FCScalculate(fullyRxPack.keys()[i])
							else:
								fullyRxPack.keys()[i].FCSbool = True
						if len(self.packRx) == 1 and self.flagTO == False and fullyRxPack.keys()[indexOffullyRxPack[0]].FCSbool == False:
							pack = fullyRxPack.keys()[indexOffullyRxPack[0]]
							self.paqReceived.append(pack)
							self.paqReceivedCorrectly += 1
							self.flagRx = False
							self.packRx.pop(pack)
							lista = [o.source for o in self.packRx.keys()]
							if pack.typeF == 'ACK':
								self.printObject.printRxACK(pack, self.env.now + self.error, 'Termina', pack.source, pack.node.name, pack.FCSbool)
								self.printObject.printTxt(pack, self.env.now + self.error, 'r', pack.node.name, pack.source, pack.totalLen, 'Termina', pack.FCSbool, '-')
							else:
								self.printObject.printRx(pack, self.env.now + self.error, lista, 'Termina', 'False', pack.FCSbool)
								self.printObject.printTxt(pack, self.env.now + self.error, 'r', pack.node.name, pack.source, pack.totalLen, 'Termina', pack.FCSbool, '-')
							if pack.typeF == "ACK" and pack.secuence == self.pack.secuence:
								yield self.env.timeout(self.error)
								if self.ACKrequestProcess.processed:
									self.printObject.printRxACK(pack, self.env.now, 'Ha caducado', pack.source, pack.node.name, '---')
								else:
									self.ACKrequestProcess.interrupt() 
									pack.ACKanswer = True
							elif (pack.typeF == "DAT" or pack.typeF == "COM") and pack.ACKrequest == True:
								self.flagACKTx = True
								yield self.env.timeout(self.error)
								time = self.env.now
								while True:
									if self.flagTx == True or self.flagRx == True:
										yield self.env.timeout(self.tsym/self.sym)
									else:
										self.txProcessACK = self.env.process(self.ackTx(pack, time))
										break
							else:
								yield self.env.timeout(self.error)
								continue
						else:
							yield self.env.timeout(self.error)
							if len(self.packRx) == 1 and self.flagTO == False and fullyRxPack.keys()[indexOffullyRxPack[0]].FCSbool == True:
								pack = fullyRxPack.keys()[indexOffullyRxPack[0]]
								self.packRx.pop(pack)
								lista = [o.source for o in self.packRx.keys()]
								if pack.typeF == 'ACK':
									self.printObject.printRxACK(pack, self.env.now, 'Termina', pack.source, pack.node.name, pack.FCSbool)
									self.printObject.printTxt(pack, self.env.now, 'r', pack.node.name, pack.source, pack.totalLen, 'Termina', pack.FCSbool, '-')
								else:
									self.printObject.printRx(pack, self.env.now, lista, 'Termina', 'False', pack.FCSbool)
									self.printObject.printTxt(pack, self.env.now, 'r', pack.node.name, pack.source, pack.totalLen, 'Termina', pack.FCSbool, '-')
							else:
								for i in indexOffullyRxPack:
									pack = fullyRxPack.keys()[i]
									self.packRx.pop(pack)
									lista = [o.source for o in self.packRx.keys()]
									if pack.typeF == 'ACK':
										self.printObject.printRxACK(pack, self.env.now, 'Termino y colisiono', pack.source, pack.node.name, 'True')
										self.printObject.printTxt(pack, self.env.now, 'dr', pack.node.name, pack.source, pack.totalLen, 'Termina', pack.FCSbool, '-')
									else:
										self.printObject.printRx(pack, self.env.now, lista, 'Termina', 'True', pack.FCSbool)
										self.printObject.printTxt(pack, self.env.now, 'dr', pack.node.name, pack.source, pack.totalLen, 'Termina', pack.FCSbool, '-')
							if len(self.packRx) == 0 :
								self.flagRx = False
								self.flagTO = False
				else:
					self.flagRxComplete = False
					yield self.env.timeout(self.tsym/self.sym)

	def IFS (self):
		if self.pack.totalLen < self.aMaxSIFSFrameSize:
			self.printObject.printIFS(self.name, self.env.now, 'Comienza', 'SIFS')
			yield self.env.timeout(self.aMinSIFSPeriod)
			self.printObject.printIFS(self.name, self.env.now, 'Termina', 'SIFS')
		else:
			self.printObject.printIFS(self.name, self.env.now, 'Comienza', 'LIFS')
			yield self.env.timeout(self.aMinLIFSPeriod)
			self.printObject.printIFS(self.name, self.env.now, 'Termina', 'LIFS')

	def auxIFS(self):
		self.IFSprocess = self.env.process(self.IFS())
		yield self.IFSprocess
		self.flagIFS = False
		if self.pack.typeF != "ACK":
			self.env.process(self.CSMA_CA_UNS())

	def ackRx(self):
		while True:
			try:
				time = self.env.now
				if (time - self.pack.txTimeStop) + self.error < self.timeToWaitAnACK and self.pack.auxFrameRetries <= self.pack.aMaxFrameRetries:
					yield self.env.timeout(self.tsym/self.sym)
				else:
					self.pack.retransmitionPack()
					if self.pack.auxFrameRetries > self.pack.aMaxFrameRetries:
						self.paqTirados += 1
						self.processAuxACKRx.interrupt('MaxRetries rebasado')
						self.printObject.printRxACK(self.pack, self.env.now, "Recepcion fallida", self.pack.node.name, self.pack.source, '---')
						self.printObject.printTx(self.pack, self.env.now, 'Se tira', self.paqsent, self.paqTirados, self.BEexp, self.auxBEexp)
						self.printObject.printTxt(self.pack, self.env.now, 'dt', self.pack.node.name, self.pack.source, self.pack.totalLen, '-', '-', self.pack.auxFrameRetries)
						self.successfulTx()
						break
					self.unsuccessfulTx (self.pack)
					self.processAuxACKRx.interrupt('ACKNotRx')
					self.printObject.printRxACK(self.pack, self.env.now, "Recepcion fallida", self.pack.node.name, self.pack.source, '---')
					break
			except simpy.Interrupt as i:
				break

	def auxACKRx(self):
		try:
			self.flagACKRx = True
			self.ACKrequestProcess = self.env.process(self.ackRx())
			yield self.ACKrequestProcess
			self.flagACKRx = False
			if self.pack.typeF != "ACK":
				self.successfulTx()
			self.flagIFS = True
			self.env.process(self.auxIFS())
		except simpy.Interrupt as i:
			self.flagTx = False
			self.flagACKRx = False
			self.env.process(self.CSMA_CA_UNS())

	def tx(self):
		try:
			self.flagTx = True
			with self.canal.wirelessMedium.request() as req:
				yield req
				self.canal.nodesTx.append(self.name)
				yield self.env.process(self.canal.intoCanal(self.pack, self. vecinos))
				if self.pack.typeF == 'ACK':
					self.printObject.printTxACK(self.pack, self.env.now, 'Comienza', 'No ha caducado', self.paqsent, self.paqTirados, self.pack.txTime - self.pack.ACKtime)
					self.printObject.printTxt(self.pack, self.env.now, 't', self.pack.node.name, self.pack.source, self.pack.totalLen, 'Comienza', '-', self.pack.auxFrameRetries)
					yield self.env.timeout(self.pack.totalLen*2*self.tsym)
				else:
					self.printObject.printTx(self.pack, self.env.now, 'Comienza', self.paqsent, self.paqTirados, self.BEexp, self.auxBEexp)
					self.printObject.printTxt(self.pack, self.env.now, 't', self.pack.node.name, self.pack.source, self.pack.totalLen, 'Comienza', '-', self.pack.auxFrameRetries)
					yield self.env.timeout(self.pack.totalLen*2*self.tsym)
				self.canal.wirelessMedium.release(req)
				self.flagTx = False
				self.txProcess= None
				self.pack.txTimeStop = self.env.now
				self.paqsent += 1
				self.canal.nodesTx.remove(self.name)
				if self.pack.typeF == 'ACK':
					self.printObject.printTxACK(self.pack, self.env.now, 'Terminado', '---', self.paqsent, self.paqTirados, self.pack.txTime - self.pack.ACKtime)
					self.printObject.printTxt(self.pack, self.env.now, 't', self.pack.node.name, self.pack.source, self.pack.totalLen, 'Termina', '-', self.pack.auxFrameRetries)
				else:
					self.printObject.printTx(self.pack, self.env.now, 'Terminado', self.paqsent, self.paqTirados, self.BEexp, self.auxBEexp)
					self.printObject.printTxt(self.pack, self.env.now, 't', self.pack.node.name, self.pack.source, self.pack.totalLen, 'Termina', '-', self.pack.auxFrameRetries)
				if self.pack.ACKrequest:
					self.processAuxACKRx = self.env.process(self.auxACKRx())
				else:
					if self.pack.typeF != "ACK":
						self.successfulTx()
					self.flagIFS = True
					self.env.process(self.auxIFS())
		except simpy.Interrupt as i:
			self.flagTx = False
			self.txProcess= None
			self.env.process(self.CSMA_CA_UNS())

	def repeatedElements(self, nodeObjectL, nodeNameL):
		listaAux = nodeNameL[:]
		lista = [o.name for o in nodeObjectL]
		listaAux.extend(lista)
		resultado = [item for item, count in collections.Counter(listaAux).items() if count > 1]
		return resultado

	def CCA (self):
		vecinosTx = self.repeatedElements(self.vecinos, self.canal.nodesTx)
		if vecinosTx:
			return False
		return True

	def EBFunction(self):
		time = 0
		while True:
			vecinosTx = self.repeatedElements(self.vecinos, self.canal.nodesTx)
			if len(vecinosTx) == 0 and self.flagTx == False and self.flagIFS == False and self.flagACKRx == False and self.flagACKTx == False:
				if time + self.error >= self.EBTime:
					break
				yield self.env.timeout(self.tsym/self.sym)
				time = time + (self.tsym/self.sym)
			elif self.flagACKTx == True:
				self.printObject.printEB(self.name, self.env.now, 'Se pausa', self.EBTime, self.BEexp, self.auxBEexp)
				if self.txProcessACK == None:
					yield self.env.timeout(self.error)
				yield self.txProcessACK
				self.printObject.printEB(self.name, self.env.now, 'Se reanuda', self.EBTime, self.BEexp, self.auxBEexp)
			elif self.flagIFS == True:
				self.printObject.printEB(self.name, self.env.now, 'Se pausa', self.EBTime, self.BEexp, self.auxBEexp)
				yield self.IFSprocess
				self.printObject.printEB(self.name, self.env.now, 'Se reanuda', self.EBTime, self.BEexp, self.auxBEexp)
			elif self.flagACKRx == True:
				self.printObject.printEB(self.name, self.env.now, 'Se pausa', self.EBTime, self.BEexp, self.auxBEexp)
				yield self.ACKrequestProcess
				self.printObject.printEB(self.name, self.env.now, 'Se reanuda', self.EBTime, self.BEexp, self.auxBEexp)
			else:
				if self.flagTx == True:
					vecinoTx = self
				else:
					vecinoTx = self.vecinos[self.getAllindexOfNodes(self.vecinos, vecinosTx[0])[0]]
				self.printObject.printEB(self.name, self.env.now, 'Se pausa', self.EBTime, self.BEexp, self.auxBEexp)
				if vecinoTx.txProcess == None:
					yield vecinoTx.txProcessACK
				elif vecinoTx.txProcessACK == None:
					yield vecinoTx.txProcess
				else:
					yield vecinoTx.txProcess & vecinoTx.txProcessACK
				self.printObject.printEB(self.name, self.env.now, 'Se reanuda', self.EBTime, self.BEexp, self.auxBEexp)

	def CSMA_CA_UNS(self):
		if self.queue and self.flagTx == False and self.flagIFS == False: 
			self.printObject.printEB(self.name, self.env.now, 'Comienza', self.EBTime, self.BEexp, self.auxBEexp)
			self.EBprocess = self.env.process(self.EBFunction())
			yield self.EBprocess
			self.printObject.printEB(self.name, self.env.now, 'Termina', self.EBTime, self.BEexp, self.auxBEexp)
			self.printObject.printCCA(self.name, self.env.now, 'Comienza', '---')
			yield self.env.timeout(self.CCAtime - self.error)
			canalState = self.CCA()
			pack = self.queue.pop(0)
			pack.setupFrame(self.env.now, self.command)
			if canalState and self.flagTx == False and self.flagIFS == False:
				self.pack = pack
				self.printObject.printCCA(self.name, self.env.now + self.error, 'Termina', 'Libre')
				self.txProcess = self.env.process(self.tx())
				yield self.txProcess
			else:
				yield self.env.timeout(self.error)
				self.printObject.printCCA(self.name, self.env.now, 'Termina', 'Ocupado')
				self.unsuccessfulTx (pack)
				self.env.process(self.CSMA_CA_UNS())
		else:
			yield self.env.timeout(self.tsym/self.sym)
			self.env.process(self.CSMA_CA_UNS())

	def setupNode (self, vecinos, command, canal, printObject):
		yield self.env.timeout(0)
		self.vecinos = vecinos
		self.command = command
		self.canal = canal
		self.printObject = printObject
		self.getEB()
		yield self.env.timeout(random.expovariate(1.0/self.timeMaxToSleep))
		self.env.process(self.putQueue())
		self.env.process(self.CSMA_CA_UNS())
		self.env.process(self.rx())