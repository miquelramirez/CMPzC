import sys
import os

from 	oob 	import OrderOfBattle
from 	units 	import Unit, morale_table
import 	n44

class Casualties :
	
	def __init__( self ) :
		self.losses = { 'INF':0, 'ART':0, 'AFV':0, 'ABN':0, 'NAV':0 }
		self.vp = { 'INF':0, 'ART':0, 'AFV':0, 'ABN':0, 'NAV':0 }

	def load_losses( self, line ) :
		fields = line.split(' ')
		self.losses['INF'] = int(fields[0])
		self.losses['ART'] = int(fields[1])
		self.losses['AFV'] = int(fields[2])
		self.losses['ABN'] = int(fields[3])
		self.losses['NAV'] = int(fields[4])
		
	def load_losses_vp( self, line ) :
		fields = line.split(' ')
		self.vp['INF'] = int(fields[0])
		self.vp['ART'] = int(fields[1])
		self.vp['AFV'] = int(fields[2])
		self.vp['ABN'] = int(fields[3])
		self.vp['NAV'] = int(fields[4])		
		
class Battle :
	
	def __init__( self, bte_file ) :
		self.filename = bte_file
		self.units = []
		self.units_db = {}
		self.side_A_casualties = Casualties()
		self.side_B_casualties = Casualties()
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
				file_lines.append( line )
		print >> sys.stdout, len(file_lines), "lines loaded from", self.filename
		
		idx = 1
		# 2. Process lines
		for line in file_lines :
			if self.oob_db is None :
				if ".oob" in line : # oob file reference found
					print >> sys.stdout, "Found reference to OOB file:", line
					self.oob_db = OrderOfBattle( line )
				if idx == 9 : # Side A losses
					self.side_A_casualties.load_losses( line )
				if idx == 10 : # Side A loss vp's
					self.side_A_casualties.load_losses_vp( line )
				if idx == 11 : # Side B losses
					self.side_A_casualties.load_losses( line )
				if idx == 12 : # Side B loss vp's
					self.side_B_casualties.load_losses_vp( line )
				idx +=1
				continue
			tokens = [ tok.strip() for tok in line.split( " " )]
			if self.oob_db is not None and tokens[0] == "1" : # Unit reference found
				u = Unit()
				u.load( tokens, self.oob_db )
				self.units.append( u )
				self.units_db[u.ID] = u
			idx += 1
			
		print >> sys.stdout, len(self.units), "units loaded from", self.filename
		
	def export_csv( self, filename ) :
		with open( filename, 'w' ) as outstream :
			header = [ 'Side', 'ID', 'Name', 'Component', 'Type', 'Movement','Size', 'X', 'Y', 'Strength', 'Morale', 'Fatigue', 'MP Spent', 'Disrupted', 'Low Ammo', 'Low Fuel', 'Mounted' ]
			print >> outstream, ",".join( header )
			for unit in self.units :
				fields = []
				fields.append( n44.get_side_name( unit.template.nationality ) )
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
				unit.X = int(fields[7])
				unit.Y = int(fields[8])
				unit.strength = int(fields[9])
				unit.fatigue = int(fields[11])
				unit.MP_spent = int(fields[12])
				unit.disrupted = fields[13].upper() == "TRUE"
				unit.low_ammo = fields[14].upper() == "TRUE"
				unit.low_fuel = fields[15].upper() == "TRUE"
				unit.mounted = fields[16].upper() == "TRUE"
	
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