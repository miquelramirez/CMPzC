import sys

class VictoryLocation :

	def __init__( self ) :
		self.X = None
		self.Y = None
		self.nationality = None
		self.value = None
		
	def load( self, tokens ) :
		self.X = int(tokens[1])
		self.Y = int(tokens[2])
		self.value = int(tokens[3])
		self.nationality = tokens[4]
	
	def write( self ) :
		tokens = [ "6" ]
		tokens += [ str(self.X) ]
		tokens += [ str(self.Y) ]
		tokens += [ str(self.value) ]
		tokens += [ str(self.nationality) ]
		return " ".join( tokens )
		
fort_types = { 	1:'Improved',
				2:'Trench',
				4:'Pillboxes',
				8:'Bunker',
				16:'Minefield',
				516:'Pillboxes & Improved',
				514:'Trench (reduced)',
				520:'Bunker & Improved'
				}

class FortifiedLocation :

	def __init__( self ) :
		self.X = None
		self.Y = None
		self.type = None
		
	def load( self, tokens ) :
		self.X = int( tokens[1] )
		self.Y = int( tokens[2] )
		try :
			self.type = fort_types[ int(tokens[3]) ]
		except KeyError :
			if int(tokens[3]) == 32768 :
				print >> sys.stdout, "Impassable hex at: (%d,%d)"%( self.X, self.Y )
				return False
			
		return True
		