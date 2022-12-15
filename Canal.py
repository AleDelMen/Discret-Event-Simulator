import random
import simpy
import time
from decimal import Decimal
from Pack import Pack

class Canal:

	def __init__(self, env, num_medium):
		self.env = env #Environment
		self.packT = [] #List of packets transmitting
		self.wirelessMedium = simpy.Resource(env, num_medium) #Resource
		self.nodesTx = [] #List of nodes transmitting
		self.error = 0.000001 #Error constant

	def intoCanal(self, pack, vecinos):
		self.packT.append(pack)
		yield self.env.timeout(self.error)
		vecinosTx = pack.node.repeatedElements(vecinos, self.nodesTx)
		if vecinosTx:
			pack.FCSbool = True