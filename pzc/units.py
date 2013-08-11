import sys
import os

morale_table = 	{
					1:'F',
					2:'E',
					3:'D',
					4:'C',
					5:'B',
					6:'A'
				}
# Loss types 'INF', 'GUN','AFV','ABN','NAV' }
service_loss_type_table = {
					'HQ':'INF',
					'INF':'INF',
					'HVY':'INF',
					'ENG':'INF',
					'ART':'GUN',
					'AA':'GUN',
					'AT':'GUN',
					'ARM':'AFV',
					'MOR':'GUN',
					'REC':'AFV',
					'HAA':'GUN',
					'ROC':'GUN',
					'MG':'INF',
					'RA':'ABN',
					'COM':'INF',
					'BAT':'NAV',
					'DES':'NAV',
					'PAR':'INF',
					'FI':'ABN',
					'BO':'ABN',
					'HBO':'ABN'
				}
				
class UnitTemplate :
	
	def __init__( self, nationality, text ) :
		self.nationality = nationality
		self.load( text )
		
	def load( self, text ) :
		# a. Split line into
		# unit data, unit template type
		unit_data, unit_template_type = [tok.strip() for tok in text.split(",")]
		self.type = unit_template_type
		
		# b. Split unit data
		# Fields are separated by spaces and the mapping is as follows:
		# 0 : ID
		# 1 : Service
		# 2 : Move Rating
		# 3 : Strength
		# 18 : Unit designation
		
		fields = [ tok.strip() for tok in unit_data.split(" ") ]
		self.ID = int(fields[0])
		self.service = fields[1]
		self.move_rating = fields[2]
		self.strength = int(fields[3])
		self.morale = int(fields[4])
		self.name = fields[18]

formation_sizes = { 	'AG':'Army Group', 
				'A':'Army', 
				'K':'Corps', 
				'D':'Division', 
				'G':'Brigade',
				'R':'Regiment', 
				'KG':'BattleGroup',
				'B':'Bn', 
				'C':'Coy', 
				'P':'Plt',
				'TF':'TaskForce'}
		
class Formation :
	
	def __init__( self ) :
		self.sub_units = []
		self.sub_formations = []
		pass
		
	def load( self, idx, lines, formations, units ) :
		curr_line = lines[idx]

		idx = self.load_formation_info( idx, lines, formations )
		
		if lines[idx] != "Begin" :
			raise RuntimeError, "Error parsing OOB: Expected start of formation at line %d"%(idx+1)
		
		idx += 1
		
		while lines[idx] != "End" :
			toks = lines[idx].split(" ")
			is_unit = False
			unit_start = 1
			nationality_override = None
			if "." in toks[0] :
				is_unit = True
			if "." in toks[1] :
				nationality_override = toks[0]
				is_unit = True
				unit_start = 2
			if is_unit: # is unit
				unit_nationality = self.nationality
				if nationality_override is not None :
					unit_nationality = nationality_override
				u = UnitTemplate( unit_nationality, " ".join( toks[unit_start:] ) )
				assert u.nationality is not None
				size_code = toks[unit_start-1].replace(".","")
				u.size = formation_sizes[size_code]
				self.sub_units.append( u )
				units[u.ID] = u
				idx += 1
			else : # begin new formation
				f = Formation()
				f.nationality = self.nationality
				idx = f.load( idx, lines, formations, units )
				self.sub_formations.append( f )
				
		return idx + 1
		
	def load_formation_info( self, idx, lines, formations ) :
		tokens = lines[idx].split( " " )
		nation_info = None
		valid = False
		fields = None
		if tokens[0] in formation_sizes.keys() :
			valid = True
			fields = tokens
		if tokens[1] in formation_sizes.keys() :
			valid = True
			nation_info = tokens[0]
			fields = tokens[1:]
		if not valid :
			raise RuntimeError, "Error parsing OOB: Could not parse formation: \nLine: %s\n%s"%(idx,lines[idx])
		if nation_info is not None :
			self.nationality = nation_info
		self.size = formation_sizes[fields[0]]
		self.ID = int(fields[1])
		self.name = " ".join( fields[3:] )
		
		formations[self.ID] = self
		
		return idx + 1

class Unit :
	
	def __init__(self) :
		pass
		
	def load( self, fields, oob ) :
		self.X = int(fields[1])
		self.Y = int(fields[2])
		self.ID = int(fields[3])
		try :
			self.template = oob.units[self.ID]
		except KeyError :
			raise RuntimeError, "Could not match unit %d with oob %s"%(self.ID,oob.filename)
		self.strength = int(fields[6])
		self.fatigue = int(fields[7])
		self.MP_spent = int(fields[8])
		self.decode_unit_flags( int(fields[9]) )
		
	def update( self, fields ) :
		fields[1] = str(self.X)
		fields[2] = str(self.Y)
		fields[6] = str(self.strength)
		fields[7] = str(self.fatigue)
		fields[8] = str(self.MP_spent)
		fields[9] = str(self.encode_unit_flags(int(fields[9])))
		
		
	def encode_unit_flags( self, value ) :
	
		if self.disrupted : value = value | 2
		if self.out_of_command or self.low_ammo : value = value | 128
		if self.isolated : value = value | 512
		if self.low_fuel : value = value | 32768
		if self.mounted : value = value | 256
		if self.fixed : value = value | 64
		
		return value
	
	def decode_unit_flags( self, value ) :
		self.disrupted = False
		if value & 2 == 2 :
			self.disrupted = True
		
		self.out_of_command = False
		self.low_ammo = False
		if value & 128 == 128 :
			if self.template.service == "HQ" :
				self.out_of_command = True
			else :
				self.low_ammo = True
				
		self.isolated = False
		if value & 512 == 512 :
			self.isolated = True
		
		self.low_fuel = False
		if value & 32768 == 32768 :
			self.low_fuel = True
		
		self.mounted = False
		if value & 256 == 256 :
			self.mounted = True
			
		self.fixed = False
		if value & 64 == 64 :
			self.fixed = True