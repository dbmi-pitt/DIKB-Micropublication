This README will briefly cover the function and motivations behind each file in this directory.

This folder, np-graphs, contains the various graphs that make up the np:Assertion and full nanopublication parts of the DIKB-Micropublications project.

The first file in this folder is "processed-dikb-ddis-for-nanopub.csv".
  This file is a stripped down version of the full processed DIKB file found in the data/mp-graphs directory.
  This contains a mapping of the claim URI to the type of claim, the subject URI, and the object URI.
  This file is used to develop the np:Assertions by the "dikb_mp_to_np_assertion.py" script in the scripts/np-scripts directory.
 
The second file in this folder is "dikb-np-assertion.trig".
  This file is in TriG format and contains all the named graphs for the np:Assertions developed by he "dikb_mp_to_np_assertion.py" script in the scripts/np-scripts directory.
  This file must be uploaded to Virtuoso 6.1 using the isql-vt loader, as Virtuoso conductor does not accept Trig format and the other formats do not keep named graphs.
  This file does not contain any information about the micropublications beyond referencing the specific claims through mp:formalizes, as a result, this file should be uploaded together with the inferred-graph-mp-oa.xml file located in data/mp-graphs.

The third file in this folder is "dikb-full-nanopublications.trig".