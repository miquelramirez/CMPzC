
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