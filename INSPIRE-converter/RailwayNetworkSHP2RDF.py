import os
import shapefile
import shapely
import re
import json

from rdflib import Graph, Literal, Namespace, RDF

INSPIRE_RN= Namespace("https://example.org/INSPIRE/RailwayNetwork#")
INSPIRE_FC = Namespace("http://inspire.ec.europa.eu/featureconcept/")
INSPIRE_CL = Namespace("https://inspire.ec.europa.eu/codelist/")
GEO_NS = Namespace('http://www.opengis.net/ont/geosparql#')
GEO_SF = Namespace('http://www.opengis.net/ont/sf#')
SCH_NS = Namespace('https://schema.org/')
W3GEO_NS = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
S2G_NS = Namespace('http://test/bridge_netwrok_management#')
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

def restart_graph(g, i):
    path = 'NATIONAL_ROAD_NETWORK_'+str(i)+'.ttl'
    g.serialize(path, format= 'ttl')
    g = Graph()
    g.bind("roadNetwork", data_ns)
    g.bind("roadProps", schema_ns)
    g.bind('inspireF', INSPIRE_FC)
    return g

def get_geosparql_relations(dei9m_string):
    de9im_pattern = ''.join(['T' if char != 'F' else char for char in dei9m_string])
    relations = []
    if re.match(r'T.TFF.FF.', de9im_pattern): relations += [GEO_NS['ehContains'], SCH_NS['geoContains']]
    if re.match(r'TFF.TFT..', de9im_pattern): relations +=  [GEO_NS['ehCoveredBy'], SCH_NS['geoCoveredBy']]
    if re.match(r'T.TFT.FF.', de9im_pattern): relations +=  [GEO_NS['ehCovers'], SCH_NS['geoCovers']]
    if re.match(r'TFFFTFFFT.', de9im_pattern): relations +=  [GEO_NS['ehEquals'],  GEO_NS['sfEquals'],  SCH_NS['geoEquals']]
    if re.match(r'TFF.FFT..', de9im_pattern): relations +=  [GEO_NS['ehInside']]
    if re.match(r'FT........', de9im_pattern): relations +=  [GEO_NS['ehMeet']]
    if re.match(r'F..T.....', de9im_pattern): relations +=  [GEO_NS['ehMeet']]
    if re.match(r'F...T....', de9im_pattern): relations +=  [GEO_NS['ehMeet']]
    if re.match(r'F...T....', de9im_pattern): relations +=  [GEO_NS['ehMeet']]
    if re.match(r'T.T...T..', de9im_pattern): relations +=  [GEO_NS['ehOverlap'], GEO_NS['sfOverlap'],  SCH_NS['geoOverlaps']]
    if re.match(r'FFTFTTTTT', de9im_pattern): relations +=  [GEO_NS['rcc8ec'], SCH_NS['geoTouches']]
    if re.match(r'TFFFTFFFT', de9im_pattern): relations +=  [GEO_NS['rcc8eq'], SCH_NS['geoEquals']]
    if re.match(r'TFFTFFTTT', de9im_pattern): relations +=  [GEO_NS['rcc8ntpp']]
    if re.match(r'TTTFFTFFT', de9im_pattern): relations +=  [GEO_NS['rcc8ntppi'],SCH_NS['geoContains']]
    if re.match(r'TTTTTTTTT', de9im_pattern): relations +=  [GEO_NS['rcc8po'], SCH_NS['geoOverlaps']]
    if re.match(r'TFFTTFTTT', de9im_pattern): relations +=  [GEO_NS['rcc8tpp'], SCH_NS['geoCoveredBy']]
    if re.match(r'TTTFTTFFT', de9im_pattern): relations +=  [GEO_NS['rcc8tppi'], SCH_NS['geoCovers']]
    if re.match(r'T.....FF.', de9im_pattern): relations +=  [GEO_NS['sfContains'],SCH_NS['geoContains']]
    if re.match(r'T.T......', de9im_pattern): relations +=  [GEO_NS['sfCrosses'], SCH_NS['geoCrosses']]
    if re.match(r'T........', de9im_pattern): relations +=  [GEO_NS['sfIntersects'], SCH_NS['geoIntersects']]
    if re.match(r'.T.......', de9im_pattern): relations +=  [GEO_NS['sfIntersects'], SCH_NS['geoIntersects']]
    if re.match(r'...T.....', de9im_pattern): relations +=  [GEO_NS['sfIntersects'], SCH_NS['geoIntersects']]
    if re.match(r'....T....', de9im_pattern): relations +=  [GEO_NS['sfIntersects'], SCH_NS['geoIntersects']]
    if re.match(r'FT.......', de9im_pattern): relations +=  [GEO_NS['sfTouches'], SCH_NS['geoTouches']]
    if re.match(r'F..T.....', de9im_pattern): relations +=  [GEO_NS['sfTouches'], SCH_NS['geoTouches']]
    if re.match(r'F...T....', de9im_pattern): relations +=  [GEO_NS['sfTouches'], SCH_NS['geoTouches']]
    if re.match(r'T.F..F...', de9im_pattern): relations +=  [GEO_NS['sfWithin'], SCH_NS['geoWithin']]

    return relations

class Converter:
    def __init__(self, orig_path, graph):
        self.orig_path = orig_path
        self.graph = graph

    def write(self, outfile=None, outformat='ttl'):
        return self.graph.serialize(destination=outfile, format=outformat)


class MissingFile(IOError):
    pass


def check_files(shapefile, ignore_prj=False):
    """Checks that the main files (.shp, .shx, .dbf, .prj)
    are present and accessible."""

    if not os.path.exists(shapefile):
        raise MissingFile('Missing .shp file')

    shape_base_name = os.path.splitext(shapefile)[0]

    shx = shape_base_name + '.shx'
    dbf = shape_base_name + '.dbf'
    prj = shape_base_name + '.prj'

    if not os.path.exists(shx):
        raise MissingFile('Missing .shx file')
    elif not os.path.exists(dbf):
        raise MissingFile('Missing .dbf file')
    elif not os.path.exists(prj) and not ignore_prj:
        raise MissingFile('Missing .prj file')


def convert(infile, id_field=None, data_ns=None, schema_ns=None, include_wgs84=True, include_relations=False):
    check_files(infile)

    linksets = []

    if data_ns is None:
        data_ns = Namespace('http://www.example.org/shape2geosparql/%s/data/' %
                            os.path.splitext(os.path.basename(infile))[0])
    else:
        data_ns = Namespace(data_ns)

    if schema_ns is None:
        schema_ns = Namespace('http://www.example.org/shape2geosparql/%s/ontology/' %
                              os.path.splitext(os.path.basename(infile))[0])
    else:
        schema_ns = Namespace(schema_ns)

    g = Graph()

    g.bind("railNetwork", data_ns)
    g.bind("railProps", schema_ns)
    g.bind('inspireF', INSPIRE_FC)

    shape = shapefile.Reader(infile).__geo_interface__
    if not shape['type'] == 'FeatureCollection': raise TypeError(shape['type'])
    
    print('creating Features')
    for feature_index in range(len(shape['features'])):
        feature = shape['features'][feature_index]
        fields = feature['properties']
         
        feature_id_str = fields['id_tramo']


        feature_id = data_ns[str(feature_id_str)]

       
        g.add((feature_id, RDF['type'], GEO_NS['Feature']))
        g.add((feature_id, RDF['type'], SCH_NS['Place']))
        g.add((feature_id, RDF['type'], INSPIRE_FC['RailwayLink']))

       

        for field_key in fields.keys():
            if field_key == 'id_lineafc':
                if fields[field_key] not in linksets:
                    linksets.append(fields[field_key])
                    g.add((data_ns[str(fields[field_key])], RDF['type'] , INSPIRE_FC['RailwayLine'] ))
                else: pass
                g.add((data_ns[str(fields[field_key])], RDFS.member , feature_id ))
            else:
                g.add((feature_id,schema_ns[field_key.lower()],Literal(fields[field_key])))

        geometry = feature['geometry']

        geom_id = data_ns[str(feature_id_str) + '_geom']
        g.add((feature_id, GEO_NS['hasGeometry'], geom_id))
        g.add((geom_id, RDF['type'], GEO_SF[geometry['type']]))
        print(geometry)
        g.add((geom_id, GEO_NS['asGeoJson'], Literal(json.dumps(geometry))))

        if include_wgs84:
            if geometry['type'] == 'point':
                # NOTE: not sure whether to use the xsd:float literal or not, see http://www.w3.org/2003/01/geo/
                g.add((geom_id, W3GEO_NS['long'], Literal(geometry['coordinates'][0])))
                g.add((geom_id, W3GEO_NS['lat'], Literal(geometry['coordinates'][1])))

    if include_relations:
        print('Creating Feature Relations')
        i=0
        for feature_index in range(len(shape['features'])):

            if feature_index-i >= 100000:
                print(feature_index)
                i += 100000
                g = restart_graph(g, feature_index)
                
            feature = shape['features'][feature_index]

            feature_id = data_ns[str(feature['properties']['id_tramo'])]

            for feature_index2 in range(len(shape['features'])):
                feature2 = shape['features'][feature_index2]
            

                feature_id2 =  data_ns[str(feature2['properties']['id_tramo'])]

                if feature_id == feature_id2: continue
                
                geos = [shapely.from_geojson(json.dumps(feature['geometry'])), shapely.from_geojson(json.dumps(feature2['geometry']))]

                de9im = shapely.relate(geos[0], geos[1])

                for relation in get_geosparql_relations(de9im):
                    g.add((feature_id, relation,  feature_id2))


    return Converter(orig_path=infile, graph=g)


schema_ns = 'http://www.example.org/Government/Networks/TransportNetworks/RailwayTransportNetworkPorperties/ontology#'
data_ns = 'http://www.example.org/Government//Networks/TransportNetworks/RailwayTransportNetwork/data/'
conversion_object = convert(infile="D:/SemTech/GeoData/Carreteras/ABOVE_A2_FFCC.shp", schema_ns=schema_ns, data_ns=data_ns, include_relations=True)
conversion_object.write("A2_Above_FFCC.ttl")



