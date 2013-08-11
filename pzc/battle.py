import sys
import os

from 	oob 		import OrderOfBattle
from 	units 		import Unit, morale_table, service_loss_type_table
from	locations	import VictoryLocation, FortifiedLocation
import 	n44

class Casualties :
	
	def __init__( self ) :
		self.losses = { 'INF':0, 'GUN':0, 'AFV':0, 'ABN':0, 'NAV':0 }
		self.vp = { 'INF':0, 'GUN':0, 'AFV':0, 'ABN':0, 'NAV':0 }

	def load_losses( self, line ) :
		fields = line.split(' ')
		self.losses['INF'] = int(fields[0])
		self.losses['GUN'] = int(fields[1])
		self.losses['AFV'] = int(fields[2])
		self.losses['ABN'] = int(fields[3])
		self.losses['NAV'] = int(fields[4])
		
	def load_losses_vp( self, line ) :
		fields = line.split(' ')
		self.vp['INF'] = int(fields[0])
		self.vp['GUN'] = int(fields[1])
		self.vp['AFV'] = int(fields[2])
		self.vp['ABN'] = int(fields[3])
		self.vp['NAV'] = int(fields[4])		
	
	def update( self, service, lost_amount ) :
		try :
			loss_type = service_loss_type_table[service]
		except KeyError :
			raise RuntimeError, "Could not determine loss type for service: %s"%service
		print >> sys.stdout, 'Updating casualties:', lost_amount, 'of type', loss_type, 'for', lost_amount * n44.Casualty_VP, 'VPs'
		self.losses[loss_type] += lost_amount
		self.vp[loss_type] += lost_amount * n44.Casualty_VP
		
	def write_losses( self, line ) :
		tokens = [ tok.strip() for tok in line.split( " " )]
		tokens[0] = str( self.losses['INF'] )
		tokens[1] = str( self.losses['GUN'] )
		tokens[2] = str( self.losses['AFV'] )
		tokens[3] = str( self.losses['ABN'] )
		tokens[4] = str( self.losses['NAV'] )
		return " ".join(tokens)
	
	def write_loss_vps( self, line ) :
		tokens = [ tok.strip() for tok in line.split( " " )]
		tokens[0] = str( self.vp['INF'] )
		tokens[1] = str( self.vp['GUN'] )
		tokens[2] = str( self.vp['AFV'] )
		tokens[3] = str( self.vp['ABN'] )
		tokens[4] = str( self.vp['NAV'] )
		return " ".join(tokens)
	
class Battle :
	
	def __init__( self, bte_file ) :
		self.filename = bte_file
		self.units = []
		self.units_db = {}
		self.units_locs = {}
		self.side_A_casualties = Casualties()
		self.side_B_casualties = Casualties()
		self.oob_db = None
		self.vp_locs = {}
		self.fort_locs = {}
		
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
		vloc_count = 0
		fortloc_count = 0
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
					self.side_B_casualties.load_losses( line )
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
				try :
					self.units_locs[ (u.X, u.Y) ] += [ u ]
				except KeyError :
					self.units_locs[ (u.X, u.Y) ] = [ u ]
			if self.oob_db is not None and tokens[0] == "6" : # Victory Location
				loc = VictoryLocation()
				loc.load( tokens )
				self.vp_locs[ (loc.X, loc.Y) ] = loc
				vloc_count += 1
			if self.oob_db is not None and tokens[0] == "10" : # Fortified Location
				loc = FortifiedLocation()
				if loc.load( tokens ) :
					self.fort_locs[ (loc.X, loc.Y) ] = loc
					fortloc_count += 1
			idx += 1
			
		print >> sys.stdout, len(self.units), "units loaded from", self.filename
		print >> sys.stdout, vloc_count, "victory locations loaded from", self.filename
		print >> sys.stdout, fortloc_count, "fortified locations loaded from", self.filename
		
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
				if fields[1] == "ID" : continue
				try :
					unit = self.units_db[ int(fields[1]) ]
				except KeyError :
					raise RuntimeError, "Unit with ID %d doesn't appear in %s"%(int(fields[1]),self.filename)
					
				self.units_locs[ (unit.X, unit.Y) ].remove( unit )
				unit.X = int(fields[7])
				unit.Y = int(fields[8])
				try :
					self.units_locs[ (unit.X, unit.Y) ] += [ unit ]
				except KeyError :
					self.units_locs[ (unit.X, unit.Y) ] = [ unit ]
					
				new_str_value = int(fields[9])
				if new_str_value < unit.strength :
					losses = unit.strength - new_str_value
					if n44.is_side_A( unit.template.nationality ) :
						self.side_A_casualties.update( unit.template.service, losses )
					elif n44.is_side_B( unit.template.nationality ) :
						self.side_B_casualties.update( unit.template.service, losses )
					else :
						raise RuntimeError, "Could not determine side for nationality: %s"%unit.template.nationality
					unit.strength = int(fields[9])
					
				unit.fatigue = int(fields[11])
				unit.MP_spent = int(fields[12])
				unit.disrupted = fields[13].upper() == "TRUE"
				unit.low_ammo = fields[14].upper() == "TRUE"
				unit.low_fuel = fields[15].upper() == "TRUE"
				unit.mounted = fields[16].upper() == "TRUE"
				
		self.update_victory_location_ownership()
	
	def update_victory_location_ownership( self ) :
		for coords, loc in self.vp_locs.iteritems() :
			units = []
			try :
				units = self.units_locs[ coords ]
			except KeyError :
				pass
			
			if len(units) == 0 : continue # No unit in hex, ownership doesn't change
			
			if loc.nationality != units[0].template.nationality :
				print >> sys.stdout, "Ownership of", coords, "changed from", loc.nationality, "to", units[0].template.nationality
				loc.nationality = units[0].template.nationality
	
	def save( self, newfilename ) :
		# 1. Load file contents into memory
		file_lines = []
		with open( self.filename ) as instream :
			for line in instream :
				line = line.strip()
				file_lines.append( line )

		# 2. Process lines
		with open( newfilename, 'w' ) as outstream :
			idx = 1
			oob_found = False
			for line in file_lines :
				if idx == 9 : # Side A casualties
					updated_line = self.side_A_casualties.write_losses( line )
					print >> outstream, updated_line
					idx += 1
					continue
				if idx == 10 :
					updated_line = self.side_A_casualties.write_loss_vps( line )
					print >> outstream, updated_line
					idx += 1
					continue
				if idx == 11 : # Side B casualties
					updated_line = self.side_B_casualties.write_losses( line )
					print >> outstream, updated_line
					idx += 1
					continue
				if idx == 12 :
					updated_line = self.side_B_casualties.write_loss_vps( line )
					print >> outstream, updated_line
					idx += 1
					continue				
				if ".oob" in line : # oob file reference found
					oob_found = True
					print >> outstream, line
					idx += 1
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
				if oob_found and tokens[0] == "6" : # Victory location found
					loc_coords = (int(tokens[1]), int(tokens[2]))
					loc = None
					try :
						loc = self.vp_locs[loc_coords]
					except KeyError :
						raise RuntimeError, "Victory location at %s wasn't loaded!"%loc_coords
					updated_line = loc.write()
					print >> outstream, updated_line
				idx += 1