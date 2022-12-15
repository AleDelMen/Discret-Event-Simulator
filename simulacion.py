import simpy
import random
from NodoPAN import NodoPAN

RANDOM_SEED = 1 #Random number to repeat the results
SIM_TIME = 100  #Simulation time
printFunctions = [False, False] #to enable or disable printing to console and text file, respectively 
timeBetweenPack = 1 #Generate a packet approximately every x seconds
probCOMFrame = 0.5 #Probability of creating a command package every time a data package is created
probError = 0.1 #Probability that a package contains errors, without considering collisions
probACK = 0.8 #Probability that a package requires ACK
nodePANName = 'A'
#First test
#grafo = {'A':['B'], 'B':['A']}
#Second test
#grafo = {'A':['B', 'C', 'D', 'E', 'F', 'G'], 'B':['A'], 'C':['A'], 'D':['A'], 'E':['A'], 'F':['A'], 'G':['A']}
#grafo = {'A':['B', 'C', 'D', 'E'], 'B':['A'], 'C':['A'], 'D':['A'], 'E':['A']}
#Third test
#grafo = {'A':['B', 'C', 'D', 'E'], 'B':['A'], 'C':['A', 'I', 'H'], 'D':['A', 'L', 'K', 'J'], 
#		 'E':['F', 'G', 'A'], 'F':['E'], 'G':['E'], 'H':['C'], 'I':[ 'C'], 'J':['D'], 'K':['D'], 
#		 'L':['D']}
#grafo = {'A':['B', 'C', 'D', 'E'], 'B':['A','U','V','W','X'], 'C':['A', 'I', 'H'], 'D':['A', 'J', 'K', 'L'], 
#		 'E':['F', 'G', 'A'], 'F':['E','T'], 'G':['E','R','S'], 'H':['C','Y','Z'], 'I':[ 'C'], 'J':['D', 'M', 'N'], 'K':['D'], 
#		 'L':['D','O','P','Q'], 'M':['J'], 'N':['6','7','8','9','J'], 'O':['1','2','3', 'L'], 'P':['L'], 'Q':['4','5','L'], 
#		 'R':['G','20','21','22','23','24'], 'S':['G'], 'T':['F'], 'U':['B','14','15','16'], 'V':['B','17','18'], 'W':['B','19'],
#		 'X':['B'], 'Y':['H','13'], 'Z':['H','12','11','10'], '1':['O'], '2':['O'], '3':['O'], '4':[ 'Q'], '5':['Q'], '6':['N'], 
#		 '7':['N'], '8':['N'], '9':['N'], '10':['Z'], '11':[ 'Z'], '12':['Z'], '13':['Y'], 
#		 '14':['U'], '15':['U'], '16':['U'], '17':['V'], '18':[ 'V'], '19':['W'], '20':['R'], 
#		 '21':['R'], '22':['R'], '23':['R'], '24':['R']}

grafo = {'A':['B', 'C', 'D', 'E'], 'B':['A','U','V','W','X'], 'C':['A', 'I', 'H'], 'D':['A', 'J','K','L'], 
		 'E':['F', 'G', 'A'], 'F':['E','T'], 'G':['E','R','S'], 'H':['C','Y','Z'], 'I':[ 'C'], 'J':['D', 'M', 'N'], 'K':['D'], 
		 'L':['D','O','P','Q'], 'M':['J'], 'N':['6','7','8','9','J'], 'O':['1','2','3', 'L'], 'P':['L'], 'Q':['4','5','L'], 
		 'R':['G','20','21','22','23','24'], 'S':['G'], 'T':['F'], 'U':['B','14','15','16'], 'V':['B','17','18'], 'W':['B','19'],
		 'X':['B'], 'Y':['H','13'], 'Z':['H','12','11','10'], '1':['O','25','26','27'], '2':['O','31'], '3':['O','28','29','30'], '4':[ 'Q','32','33'], '5':['Q','34','35','36','37'], '6':['N','38'], 
		 '7':['N','39'], '8':['N','40','41'], '9':['N','42','44','43'], '10':['Z','45','46','47','48'], '11':[ 'Z'], '12':['Z','49','50'], '13':['Y','51','52','53','54'], 
		 '14':['U','58','59'], '15':['U','60'], '16':['U','61','62','63'], '17':['V','57'], '18':[ 'V','56'], '19':['W','55'], '20':['R','64','65'], 
		 '21':['R','66', '67'], '22':['R','68','69','70'], '23':['R','71','72'], '24':['R','73','74'], '25':['1'], '26':['1'], '27':['1'], '28':[ '3'], '29':['3'], '30':['3'], 
		 '31':['2'], '32':['4'], '33':['4'], '34':['5'], '35':[ '5'], '36':['5'], '37':['5'], 
		 '38':['6'], '39':['7'], '40':['8'], '41':['8'], '42':[ '9'], '43':['9'], '44':['9'], 
		 '45':['10'], '46':['10'], '47':['10'], '48':['10'], '49':['12'], '50':['12'], '51':['13'], '52':[ '13'], '53':['13'], '54':['13'], 
		 '55':['19'], '56':['18'], '57':['17'], '58':['14'], '59':[ '14'], '60':['15'], '61':['16'], 
		 '62':['16'], '63':['16'], '64':['20'], '65':['20'], '66':[ '21'], '67':['21'], '68':['22'], 
		 '69':['22'], '70':['22'], '71':['23'], '72':['23'], '73':['24'], '74':['24']}





print('\nStart the simulation')
random.seed(RANDOM_SEED)
probabilities = [probCOMFrame, probError, probACK] #Probabilities list
f = open ('Registro.txt', 'w')#The file where the information will be placed is created
f.close()
env = simpy.Environment() #The simulation environment is created
NodoPAN = NodoPAN(env, 1, True, nodePANName, grafo, printFunctions, probabilities, timeBetweenPack) #PAN node is created
NodoPAN.nodes.append(NodoPAN)
env.process(NodoPAN.makeNetwork())#The rest of the nodes are created together with the network
env.run(until=SIM_TIME)
print('\nFinish the simulation')