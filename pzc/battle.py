import sys
import os

from oob 	import OrderOfBattle
from units 	import Unit, morale_table

class Battle :
	
	def __init__( self, bte_file ) :
		self.filename = bte_file
		self.units = []
		self.units_db = {}
		self.oob_db = None
		# check that the file actually exists
		if not os.path.exists( self.filename ) :
			raise RuntimeError, "Could not open battle file: %s"%self.filename
		self.load_file( )
		
	def load_file( self ) :
		# 1. Load file contents into memory
		file_lines = []
		with open( self.filename ) as instream :
			for line in instream :
				line = line.strip()
				if len(line) == 0 : continue
				file_lines.append( line )
		print >> sys.stdout, len(file_lines), "lines loaded from", self.filename
		
		# 2. Process lines
		for line in file_lines :
			if ".oob" in line : # oob file reference found
				print >> sys.stdout, "Found reference to OOB file:", line
				self.oob_db = OrderOfBattle( line )
				continue
			tokens = [ tok.strip() for tok in line.split( " " )]
			if self.oob_db is not None and tokens[0] == "1" : # Unit reference found
				u = Unit()
				u.load( tokens, self.oob_db )
				self.units.append( u )
				self.units_db[u.ID] = u
			
		print >> sys.stdout, len(self.units), "units loaded from", self.filename
		
	def export_csv( self, filename ) :
		with open( filename, 'w' ) as outstream :
			header = [ 'ID', 'Name', 'Component', 'Type', 'Movement','Size', 'X', 'Y', 'Strength', 'Morale', 'Fatigue', 'MP Spent', 'Disrupted', 'Low Ammo', 'Low Fuel', 'Mounted' ]
			print >> outstream, ",".join( header )
			for unit in self.units :
				fields = []
				fields.append( str(unit.template.ID) )
				fields.append( unit.template.name )
				fields.append( unit.template.type )
				fields.append( unit.template.service )
				fields.append( unit.template.move_rating )
				fields.append( unit.template.size )
				fields.append( str(unit.X) )
				fields.append( str(unit.Y) )
				fields.append( str(unit.strength) )
				fields.append( morale_table[unit.template.morale] )
				fields.append( str(unit.fatigue) )
				fields.append( str(unit.MP_spent) )
				fields.append( str(unit.disrupted) )
				fields.append( str(unit.low_ammo) )
				fields.append( str(unit.low_fuel) )
				fields.append( str(unit.mounted) )
				print >> outstream, ",".join( fields )
				
	def apply_csv( self, filename ) :
		with open( filename, 'r' ) as instream :
			for line in instream :
				line = line.strip()
				if len(line) == 0 : continue
				fields = line.split( "," )
				if fields[0] == "ID" : continue
				try :
					unit = self.units_db[ int(fields[0]) ]
				except KeyError :
					raise RuntimeError, "Unit with ID %d doesn't appear in %s"%(int(fields[0]),self.filename)
				unit.X = int(fields[6])
				unit.Y = int(fields[7])
				unit.strength = int(fields[8])
				unit.fatigue = int(fields[10])
				unit.MP_spent = int(fields[11])
				unit.disrupted = fields[12].upper() == "TRUE"
				unit.low_ammo = fields[13].upper() == "TRUE"
				unit.low_fuel = fields[14].upper() == "TRUE"
				unit.mounted = fields[15].upper() == "TRUE"
	
	def save( self, newfilename ) :
		# 1. Load file contents into memory
		file_lines = []
		with open( self.filename ) as instream :
			for line in instream :
				line = line.strip()
				file_lines.append( line )
		
		# 2. Process lines
		with open( newfilename, 'w' ) as outstream :
			oob_found = False
			for line in file_lines :
				if ".oob" in line : # oob file reference found
					oob_found = True
					print >> outstream, line
					continue
				tokens = [ tok.strip() for tok in line.split( " " )]
				if oob_found and tokens[0] == "1" : # Unit reference found
					
					try :
						unit = self.units_db[int(tokens[3])]
					except KeyError :
						raise RuntimeError, "Unit %d in %s could not be matched while saving!"%(int(tokens[3]), self.filename)
					unit.update( tokens )
					print >> outstream, " ".join( tokens )
				else :
					print >> outstream, line