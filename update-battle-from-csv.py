import os
import sys
from pzc.battle import Battle

def main() :
	if len(sys.argv) != 4 :
		print >> sys.stderr, "No battle file (.bte) was specified!"
		print >> sys.stderr, "Usage: extract-to-csv.py <.csv file> <.bte file> <.bte file>"
		sys.exit(1)
	
	battle_file = Battle( sys.argv[2] )
	battle_file.apply_csv( sys.argv[1] )
	battle_file.save( sys.argv[3] )

if __name__ == '__main__' :
	main()