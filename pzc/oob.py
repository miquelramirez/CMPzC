import sys
import os
from units import UnitTemplate, Formation

oob_dir = "data\Normandy-44"

class OrderOfBattle :

	def __init__( self, oob_file ) :
		self.filename = os.path.join( oob_dir, oob_file )
		self.units = {}
		self.formations = {}
		self.top_level_formations = []
		if not os.path.exists( self.filename ) :
			raise RuntimeError, "Could not open oob file: %s"%self.filename
		self.load_file( )
		
	def load_file( self ) :
		# 1. Load file contents into memory
		file_lines = []
		with open( self.filename ) as instream :
			for line in instream :
				line = line.strip()
				file_lines.append( line )
		print >> sys.stdout, len(file_lines), "lines loaded from", self.filename
		
		# 2. Process lines
		num_lines = len(file_lines)
		current = 2
		while current < num_lines :
			f = Formation()
			current = f.load( current, file_lines, self.formations, self.units ) # Load a formation
			self.top_level_formations.append( f )
		
		print >> sys.stdout, len(self.formations), "formations loaded from oob"
		print >> sys.stdout, len(self.units), "units loaded from oob"