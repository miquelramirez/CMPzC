
Side_A_Name = "Allies"
Side_A_Nations = ["American", "American-AB", "British", "Canadian", "French", "Polish"]

Side_B_Name = "Axis"
Side_B_Nations = [ "German", "German-SS" ]

Casualty_VP = 15

def is_side_A( nation ) :
	return nation in Side_A_Nations
	
def is_side_B( nation ) :
	return nation in Side_B_Nations
	
def get_side_name( nation ) :
	if nation in Side_A_Nations : return Side_A_Name
	if nation in Side_B_Nations : return Side_B_Name
	raise RuntimeError, "Nationality %s doesn't belong to any side"%nation