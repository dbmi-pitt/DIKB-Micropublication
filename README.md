DIKB-Micropublication

=====================

Micropublication and Open Data Annotation for drug-drug interaction evidence synthesis

=====================

OBJECTIVE

The purpose of this project is to test various models for representing
drug-drug interactions claims using Micropublication, Open Data
Annotation, and the new Drug Interaction Data and Evidence Ontology
(DIDEO)

=====================

TEAM MEMBERS

Principal Investigators: Richard D Boyce, Phd
Lead Programmer: Yifan Ning, MS
Collaborators/Co-Investigators: Jodi Schneider, PhD, Samuel Rosko, Tim Clark, PhD, Paolo Ciccarese, PhD, Paul Groth, PhD


=====================

ACKNOWLEDGEMENTS

This project is supported by a grant from the National Library of
Medicine: "Addressing gaps in clinically useful evidence on drug-drug
interactions" (1R01LM011838-01)

=====================

PUBLICATIONS

Schneider, J., Brochhausen, M., Rosko, S., Ciccarese, S., Hogan, WR., Malone, D., Ning, Y., Clark, T., and Boyce, RD. Formalizing knowledge and evidence about potential drug-drug interactions. The International Workshop on Biomedical Data Mining, Modeling, and Semantic Integration: A Promising Approach to Solving Unmet Medical Needs (BDM2I 2015) at the 14th International Semantic Web Conference (ISWC). October 11th 2015. Bethlehem, PA. http://ceur-ws.org/Vol-1428/BDM2I_2015_paper_10.pdf.

Schneider, J., Collins, C., Hines, L., Horn, JR, Boyce, R. “Modeling Arguments in Scientific Papers.” at the 12th Annual ArgDiaP Conference: From Real Data to Argument Mining. Warsaw, Poland, May 23-24 2014. http://jodischneider.com/pubs/argdiap2014.pdf

Schneider, J., Ciccarese, P., Clark, T., Boyce, RD. Using the Micropublications ontology and the Open Annotation Data Model to represent evidence within a drug-drug interaction knowledge base. The 4th Workshop on Linked Science 2014— Making Sense Out of Data (LISC2014). Collocated with the 13th International Semantic Web Conference (ISWC2014). October 19th and 20th, Riva del Garda, Trentino, Italy. http://ceur-ws.org/Vol-1282/.

=====================

MP/NP EXAMPLES (https://dbmi-icode-01.dbmi.pitt.edu/sparql)

A NP:
```
select *
from <ddi:ddi-spl-annotation-np-head-389>
where {
 ?s ?p ?o.
}
```

```
DESCRIBE <http://dbmi-icode-01.dbmi.pitt.edu/mp/ddi-spl-annotation-claim-1>
```
Or, view the queries in the [example queries](queries/)


