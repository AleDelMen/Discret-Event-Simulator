class printClass:
	def __init__(self, pConsole, pTxt):
		self.printConsole = pConsole #Flag to enable or disable console printing
		self.printTxtBool = pTxt #Flag to enable or disable txt printing
	#Funciones para imprimir en consola

	def printPack(self, pack, time):
		if self.printConsole == True:
			print('====================================================================')
			print('Accion: {action}\t Requiere ACK: {ACK}'.format(action='Creacion de paquete', ACK=pack.ACKrequest))
			print('Tipo de paquete: {pack}\t\t Nodo Rx: {nodeRx}'.format(pack=pack.typeF, nodeRx=pack.node.name))
			print('Nodo Tx: {node}\t\t\t Numero de secuencia:{numberSec}'.format(node=pack.source, numberSec=pack.secuence))
			print('Tiempo: {time}'.format(time=time))
			print('====================================================================')
			#raw_input("Pulsa una tecla para continuar...")

	def printTx(self, pack, time, status, paqsent, paqTirados, BEexp, auxBEexp):
		if self.printConsole == True:
			print('====================================================================')
			print('Accion: {action}\t\t Tamano en Bytes del paquete: {packLen}'.format(action='Transmision', packLen=pack.totalLen))
			print('Tipo de paquete: {pack}\t\t Requiere ACK: {ACK}'.format(pack=pack.typeF, ACK=pack.ACKrequest))
			print('Nodo Tx: {node}\t\t\t Numero de secuencia:{numberSec}'.format(node=pack.source, numberSec=pack.secuence))
			print('Numero de retransmision: {numberRet}\t Estatus: {status}'.format(numberRet=pack.auxFrameRetries, status=status))
			print('EB:{EB}\t\t\t\t Paquetes Tirados:{packFailed}'.format(EB=BEexp, packFailed=paqTirados))
			print('Repeticiones del EB maximo:{NB}\t Paquetes Tx:{packTx} '.format(NB=auxBEexp, packTx=paqsent))
			print('Nodo Rx: {nodeRx}\t\t\t Tiempo: {time}'.format(nodeRx=pack.node.name, time=time))
			print('====================================================================')
			#raw_input("Pulsa una tecla para continuar...")

	def printTxACK(self, pack, time, status, caducidad, paqsent, paqTirados, ACKtime):
		if self.printConsole == True:
			print('====================================================================')
			print('Accion: {action}\t\t Paquetes Tx:{packTx}'.format(action='Transmision', packTx=paqsent))
			print('Nodo Tx: {node}\t\t\t Ha caducado: {Caducidad}'.format(node=pack.source, Caducidad=caducidad))
			print('Tipo de paquete: {pack}\t\t Tiempo de ACK:{Wtime}'.format(pack=pack.typeF, Wtime=ACKtime))
			print('Tamano en Bytes del paquete: {packLen}\t Estatus: {status}'.format(packLen='11', status=status))
			print('Numero de secuencia:{numberSec}\t\t Paquetes Tirados:{packFailed}'.format(numberSec=pack.secuence, packFailed=paqTirados))
			print('Nodo Rx:{Rx}\t\t\t Tiempo: {time}'.format(Rx=pack.node.name, time=time))
			print('====================================================================')
			#raw_input("Pulsa una tecla para continuar...")

	def printRx(self, pack, time, lista, status, col, errores):
		if self.printConsole == True:
			print('====================================================================')
			print('Accion: {action}\t\t Estatus: {status}'.format(action='Recepcion', status=status))
			print('Tipo de paquete: {pack}\t\t Requiera ACK: {ACK}'.format(pack=pack.typeF, ACK=pack.ACKrequest))
			print('Nodo Rx: {node}\t\t\t Contiene errores: {FCS}'.format(node=pack.node.name, FCS=errores))
			print('Nodo Tx del paquete: {nodeRx}\t\t Colisiono: {col}'.format(nodeRx=pack.source, col=col))
			print('Numero de secuencia:{numberSec}\t\t Paquetes Rx:{packRx}'.format(numberSec=pack.secuence, packRx=pack.node.paqReceivedCorrectly))
			print('Nodos Tx: {lista}'.format(lista=lista))
			print('Tiempo: {time}'.format(time=time))
			print('====================================================================')
			#raw_input("Pulsa una tecla para continuar...")

	def printRxACK(self, pack, time, status, Tx, Rx, errores):
		if self.printConsole == True:
			print('====================================================================')
			print('Accion: {action}\t\t Estatus: {status}'.format(action='Recepcion', status=status))
			print('Nodo Tx: {nodeTx}\t\t\t Tipo de paquete: {pack}'.format(nodeTx= Tx, pack='ACK'))
			print('Nodo Rx: {node}\t\t\t Numero de secuencia:{numberSec}'.format(node= Rx, numberSec=pack.secuence))
			print('Contiene errores: {FCS}\t\t Tiempo: {time}'.format(FCS=errores, time=time))
			print('====================================================================')
			#raw_input("Pulsa una tecla para continuar...")

	def printCCA(self, node, time, status, canal):
		if self.printConsole == True:
			print('====================================================================')
			print('Accion: {action}\t\t\t Estatus: {status}'.format(action='CCA', status=status))
			print('Nodo: {node}\t\t\t\t Estado del canal: {canal}'.format(node=node, canal=canal))
			print('Tiempo: {time}'.format(time=time))
			print('====================================================================')
			#raw_input("Pulsa una tecla para continuar...")

	def printEB(self, node, time, status, timeEB, BEexp, auxBEexp):
		if self.printConsole == True:
			print('====================================================================')
			print('Accion: {action}\t\t\t Estatus: {status}'.format(action='EB', status=status))
			print('Nodo: {node}\t\t\t\t Tiempo EB:{timeEB}'.format(node=node, timeEB=timeEB))
			print('EB:{EB}\t\t\t\t Repeticiones del EB maximo:{NB}'.format(EB=BEexp, NB=auxBEexp))
			print('Tiempo: {time}'.format(time=time))
			print('====================================================================')
			#raw_input("Pulsa una tecla para continuar...")

	def printIFS(self, node, time, status, action):
		if self.printConsole == True:
			print('====================================================================')
			print('Accion: {action}\t\t\t Estatus: {status}'.format(action=action, status=status))
			print('Nodo: {node}\t\t\t\t Tiempo: {time}'.format(node=node, time=time))
			print('====================================================================')
			#raw_input("Pulsa una tecla para continuar...")

	def printCol(self, node, time, nodoRx):
		if self.printConsole == True:
			print('====================================================================')
			print('Accion: {status}\t\t Nodo Rx: {nodoRx}'.format(status='Colision', nodoRx=nodoRx))
			print('Nodo Tx: {node}\t\t\t Tiempo: {time}'.format(node=node, time=time))
			print('====================================================================')
			#raw_input("Pulsa una tecla para continuar...")

	#Funciones para imprimir en el documento	

	def printTxt(self, pack, time, action, Rx, Tx, tamano, status, errores, retransmision):
		if self.printTxtBool == True:
			f = open ('Registro.txt', 'a')
			f.write('{accion}\t {nodoTx}\t {nodoRx}\t {pack}\t {retransmision}\t {errores}\t {tamano}\t {status}\t {tiempo}\n'.format(
				accion=action, nodoTx=Tx, nodoRx=Rx, pack=pack.typeF, tamano=tamano, status=status, tiempo=time, errores=errores, retransmision=retransmision))
			f.close()