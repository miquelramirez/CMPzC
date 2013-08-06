import os
import sys
from pzc.battle import Battle

def main() :
	if len(sys.argv) != 3 :
		print >> sys.stderr, "No battle file (.bte) was specified!"
		print >> sys.stderr, "Usage: extract-to-csv.py <.bte file> <.csv file>"
		sys.exit(1)
	
	battle_file = Battle( sys.argv[1] )
	battle_file.export_csv( sys.argv[2] )

if __name__ == '__main__' :
	main()