import random
from ICDD import *

## CREATE INSPECTION CONTAINER

## Generate documenta
report = InternalDocument(
    path = "data/Inspection_report.docx",
    requested = True, 
)
inspection_graph = InternalDocument(
    path = "data/inspection_202310.ttl",
    requested = True, 
)
doc = ExternalDocument(
    url= 'https://www.fomento.gob.es/AZ.BBMF.Web/documentacion/pdf/RE2031.pdf'
)
images_path = 'data/IMAGES/'
images = []
img_directory = os.fsdecode(images_path)
img_paths = []
for file in os.listdir(img_directory):
    filename = os.fsdecode(file)
    img_path = os.path.join(images_path, filename)
    img_paths.append(img_path)
    images.append(InternalDocument(
        path = img_path
    ))

# Create Container and add metadata
container = Container(id = uuid.UUID('fb7f85bd-f2d3-4c6e-9ff7-6ccd5461a151'))
container.add_document(report)
container.add_document(inspection_graph)
container.add_document(doc)

for img in images:
    container.add_document(img)

#Generate links for docs
linkset_docs = Linkset()
identifier = URIBasedIdentifier(uri='http://0.0.0.0:5004/strata/stratum-2/graph/inspection202310_doc')
graph_linkel = LinkElement(document = inspection_graph, identifier = identifier)
doc_linkel = LinkElement(document = doc)
report_linkel = LinkElement(document = report)
link1 = Link(graph_linkel, doc_linkel)
link2 = Link(graph_linkel, report_linkel)
linkset_docs.add_link(link1)
linkset_docs.add_link(link2)

#Generate links for images
linkset_img = Linkset()
for i in range(22):
    identifier = URIBasedIdentifier(uri = 'http://0.0.0.0:5004/strata/stratum-2/graph/damage-202410-' + str(i+1))
    graph_linkel = LinkElement(document = inspection_graph, identifier = identifier)
    img_linkel = LinkElement(document = images[random.randint(0, len(images)-1)])
    link = Link(graph_linkel, img_linkel)
    linkset_img.add_link(link)

container.add_linkset(linkset_img)
container.add_linkset(linkset_docs)

container.create()
