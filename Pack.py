import random

class Pack:
	def __init__(self, typeF, secuence, node, source, idPAN):
		self.lenHeader = 0#Byte size of the header
		self.lenPay = 0#Byte size of the payload
		self.lenFCS =0 #Byte size of the FCS
		self.auxFrameRetries = 0 #Number of forwardings per package
		self.typeF = typeF #Frame type
		self.aMaxFrameRetries = 3 #Maximum number of retransmissions
		self.secuence = secuence #Sequence number
		self.txTimeStop = 0 #Time the packet stopped transmitting
		self.node = node #Recipient node object
		self.source = source #Name node source
		self.idPAN = idPAN #Identifier of the source network
		self.lenPHY = 6 #PHY layer data bytes
		self.ACKtime = 0 #Time an ACK frame spends on the source device
		self.totalLen = 0 #Total length of the frame
		self.ACKrequest = False #Boolean ACK request variable
		self.ACKanswer = False #Boolean ACK commit variable
		self.flag = False #Flag to know if the package values have been initialized
		self.FCSbool = None #Flag to know if a package has errors

	def retransmitionPack(self):
		self.auxFrameRetries += 1

	def makeHeader(self):
		if self.typeF == "ACK" :
			self.lenHeader = 2+1
		elif self.typeF == "BEA":
			self.lenHeader = 2+1+10
		else:
			self.lenHeader = 2+1+20

	def beaconFrame(self):
		self.lenPay = 2 + random.randrange(60, 120)

	def dataFrame(self):
		self.lenPay = random.randrange(61, 122)

	def ackFrame(self):
		self.lenPay = 0

	def commandFrame(self, command):
		commandTypes = ["Association request", "Association response", "Disassociation notification",
		"Data Request", "PAN ID conflict notification", "Orphan notification", "Coordinator realigment",
		"Beacon Request", "GTS request"]
		self.lenPay = 1 + random.randrange(60, 121)

	def makePayload(self, command):
		if self.typeF == "ACK":
			self.ackFrame()

		elif self.typeF == "BEA":
			self.beaconFrame()

		elif self.typeF == "COM":
			self.commandFrame(random.choice(command))

		else:
			self.dataFrame()

	def makeFCS(self):
		self.lenFCS = 2

	def setupFrame(self, txTime, command):
		if self.flag == False:
			self.makeHeader()
			self.makePayload(command)
			self.makeFCS()
			self.totalLen = self.lenHeader + self.lenPay + self.lenFCS + self.lenPHY
			self.flag = True
		self.FCSbool = None 
		self.txTime = txTime