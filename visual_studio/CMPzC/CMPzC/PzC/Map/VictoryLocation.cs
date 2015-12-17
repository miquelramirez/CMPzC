using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace CMPzC.PzC.Map
{
    public class VictoryLocation : Location
    {
        int    value;
        string nationality;

        VictoryLocation( )
            : base()
        {
            value = 0;
            nationality = null;
        }
        
        // Loads victory location from tokenized data.
        //
        // tokens[0]: code to denote victory location
        // tokens[1]: X coordinate of location
        // tokens[2]: Y coordinate of location
        // tokens[3]: points awarded for holding this location at the end of the game
        // tokens[4]: string encoding the nationality currently holding the location
        void load( List<String> tokens )
        {
            x = Int32.Parse(tokens[1]);
            y = Int32.Parse(tokens[2]);
            value = Int32.Parse(tokens[3]);
            nationality = tokens[4];
        }

        // Populates list argument so that its elements
        // correspond to the tokens encoding this location
        // data
        void write( List<String> tokens )
        {
            tokens[0] = "6"; // The code for a VL
            tokens[1] = x.ToString();
            tokens[2] = y.ToString();
            tokens[3] = value.ToString();
            tokens[4] = nationality;
        }
    }
}
