# IFC to Knowledge Graph
The IFC2KG converter is developed to convert IFC files to RDF files using multiple ontologies that are suitable to represents teh classes, attributes and relations defined in the IFC schema.

## How to Use
1. **Installation**:
   - Install python in your machine
   - clone this repository
   - Install requirements : [ifcopenshell](https://ifcopenshell.org/), [rdflib](https://rdflib.readthedocs.io/en/stable/index.html)

2. **Usage**:
   - Run the script  either from the command line or from your prefered code editor. Each converter use a config.json file (explained below).
   - The conversion-map.json file contains the mapping between the IFC entities and the BEO entities and it is the base for both converters.

4. **Configuration IFC to RDF converter ([IFC-converter](https://github.com/cramonell/beo/tree/main/IFC-converter))**:
   - *ifc-file-path*
   - *rdf-ouput*
        - *output-path*: path were the output file will be saved
        - *output-name*: name that will be used for the output graph file, the output geometry file, and will be appended to the base url
        - *ouput-format*: file format (ttl, nt, rdf/xml ...)
        - *base-url*: base url for the graph instances
    - *geometry-ouput*
        - *output-path*: path were the output file will be saved
        - *convert*: wether the geomtry should be included or not (true/flase)
        - *ouput-format*: geometry  format ( .ifc, .glb, .obj) --> NOT IMPLEMENTED
        - *split*: wether the geomtry of each is stored in a different file (true/flase)--> NOT IMPLEMENTED

5. **License**:
   - This project is licensed under the GNU General Public License (GNU GPL). You can find the full text of the license in the LICENSE.txt file.

## Conversion Map

The conversion map is contained in the *conversion-map.json* file. This file contains a structure as shown in the following snippet: 

```json
 "IfcBridge": {
        "class": [
            "https://w3id.org/bot#Zone",
            "https://w3id.org/brot#Bridge"
        ],
        "enum": {
            "CANTILEVER": [
                "https://w3id.org/brot#Bridge",
                "https://w3id.org/bridge#BeamBridge"
            ],
            "FRAMEWORK": [
                "https://w3id.org/brot#Bridge",
                "https://w3id.org/bridge#BeamBridge"
            ],
            "GIRDER": [
                "https://w3id.org/brot#Bridge",
                "https://w3id.org/bridge#GirderBridge",
                "https://w3id.org/bridge#BeamBridge"
            ]
        },
        "attrs": {
            "GlobalId": "https://w3id.org/bot#ID",
            "Name": "https://w3id.org/bot#Name",
            "Description": "https://w3id.org/bot#Description"
        },
        "inv_attrs": {
            "ContainsElements": "https://w3id.org/bot#ContainsElement"
        }
    }
```
This is the way the converter associates the classes, attributes, inverse relations, and enumerations to existing ontologies.

At the moment, the following ontologies are considered for  the conversion:

| Name | URI | 
| :------------ | :--------------: 
| Building Topology Ontology | [https://www.w3id.org/bot](https://www.w3id.org/bot)
| Built Element Ontology | [https://www.w3id.org/beo](https://www.w3id.org/beo)
| Distribution Element Ontology | [https://www.w3id.org/mep](https://cramonell.github.io/mep/actual/index-en.html)
| Bridge Topology Ontology | [https://www.w3id.org/brot](https://www.w3id.org/brot)
| Bridge Ontology | [https://www.w3id.org/bridge](https://www.w3id.org/bridge)

The idea is that the user of the onverter can customize  this JSON file to adpat the conversion to their own needs, using other ontologies.

The geometric information is linked to the resulting RDF graph using the fillowing ontologies:

| Name | URI | 
| :------------ | :--------------: 
| File Ontology for Geometry formats | [https://www.w3id.org/fog](https://www.w3id.org/fog)
| Built Element Ontology | [https://www.w3id.org/omg](https://www.w3id.org/omg)
| Geometry Metadata Ontology| [https://www.w3id.org/gom](https://www.w3id.org/gom)

## To Do List:

1. Add Material conversions.
2. Add different options for  converting geometry: Different geometry formats and also in-graph embedded geometry.
3. Add Property and Quantity Sets conversions.

## Contact
For further assistance, questions, or feedback, you can reach out to us by email to  [carlos.ramonell@upc.edu](mailto:carlos.ramonell@upc.edu)
