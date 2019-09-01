# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['conceptnet_lite']

package_data = \
{'': ['*']}

install_requires = \
['lmdb>=0.97.0,<0.98.0',
 'peewee>=3.10,<4.0',
 'pySmartDL>=1.3,<2.0',
 'tqdm>=4.35,<5.0']

setup_kwargs = {
    'name': 'conceptnet-lite',
    'version': '0.1.11',
    'description': 'Python library to work with ConceptNet offline without the need of PostgreSQL',
    'long_description': '# conceptnet-lite\n\nConceptnet-lite is a Python library for working with ConceptNet offline without the need for PostgreSQL.\n\nThe basic usage is as follows.\n\n## Loading the database object\n\nConceptNet releases happen once a year. You can build your own database from an assertions file, but if there is a pre-built file it will be faster to just download that one. Here is the [compressed database file](todo) for ConceptNet 5.7 release.\n\n```python\nimport conceptnet_lite\n\nconceptnet_lite.connect(\'/path/to/conceptnet.db\')\n```\n\n## Building the database for a new release.\n\nThe assertion files for ConceptNet are provided [here](https://github.com/commonsense/conceptnet5/wiki/Downloads).\n\n(building instructions TBA)\n\n## Accessing concepts\n\nConcepts objects are created by looking for every entry that matches the input string exactly.\nIf none is found, the `peewee.DoesNotExist` exception will be raised.\n\n```python\nfrom conceptnet_lite import Label\n\ncat_concepts = Label.get(text=\'cat\').concepts  #\nfor c in cat_concepts:\n    print("    Concept URI:", c.uri)\n    print("    Concept text:", c.text)\n```\n\n`concept.uri` provides access to ConceptNet URIs, as described [here](https://github.com/commonsense/conceptnet5/wiki/URI-hierarchy). You can also retrieve only the text of the entry by `concept.text`.\n\n## Working with languages\n\nYou can limit the languages to search for matches. Label.get() takes an optional `language` attribute that is expected to be an instance `Language`, which in turn is created by calling `Language.get()` with `name` argument.\nList of available languages and their codes are described [here](https://github.com/commonsense/conceptnet5/wiki/Languages).\n\n```python\nfrom conceptnet_lite import Label, Language\n\nenglish = Language.get(name=\'en\')\ncat_concepts = Label.get(text=\'cat\', language=english).concepts  #\nfor c in cat_concepts:\n    print("    Concept URI:", c.uri)\n    print("    Concept text:", c.text)\n    print("    Concept language:", c.language.name)\n```\n\n## Querying edges between concepts\n\nTo retrieve the set of relations between two concepts, you need to create the concept objects (optionally specifying the language as described above). `cn.edges_between()` method retrieves all edges between the specified concepts. You can access its URI and a number of attributes, as shown below.\n\nSome ConceptNet relations are symmetrical: for example, the antonymy between *white* and *black* works both ways. Some relations are asymmetrical: e.g. the relation between *cat* and *mammal* is either hyponymy or hyperonymy, depending on the direction. The `two_way` argument lets you choose whether the query should be symmetrical or not.\n\n```python\nfrom conceptnet_lite import Label, Language, edges_between\n\nenglish = Language.get(name=\'en\')\nintrovert_concepts = Label.get(text=\'introvert\', language=english).concepts\nextrovert_concepts = Label.get(text=\'extrovert\', language=english).concepts\nfor e in edges_between(introvert_concepts, extrovert_concepts, two_way=False):\n    print("  Edge URI:", e.uri)\n    print(e.relation.name, e.start.text, e.end.text, e.etc)\n```\n* **e.relation.name**: the name of ConceptNet relation. Full list [here](https://github.com/commonsense/conceptnet5/wiki/Relations).\n\n* **e.start.text, e.end.text**: the source and the target concepts in the edge\n\n* **e.etc**: the ConceptNet [metadata](https://github.com/commonsense/conceptnet5/wiki/Edges) dictionary contains the source dataset, sources, weight, and license. For example, the introvert:extrovert edge for English contains the following metadata:\n\n```json\n{\n\t"dataset": "/d/wiktionary/en",\n\t"license": "cc:by-sa/4.0",\n\t"sources": [{\n\t\t"contributor": "/s/resource/wiktionary/en",\n\t\t"process": "/s/process/wikiparsec/2"\n\t}, {\n\t\t"contributor": "/s/resource/wiktionary/fr",\n\t\t"process": "/s/process/wikiparsec/2"\n\t}],\n\t"weight": 2.0\n}\n```\n\n## Accessing all relations for a given concepts\n\nYou can also retrieve all relations between a given concepts and all other concepts, with the same options as above:\n\n```python\nfrom conceptnet_lite import Label, Language, edges_for\n\nenglish = Language.get(name=\'en\')\nfor e in edges_for(Label.get(text=\'introvert\', language=english).concepts, same_language=True):\n    print("  Edge URI:", e.uri)\n    print(e.relation.name, e.start.text, e.end.text, e.etc)\n```\n\nNote that we have used optional argument `same_language=True`. By supplying this argument we make `edges_for` return\nrelations, both ends of which are in the same language. If this argument is skipped it is possible to get edges to\nconcepts in languages other than the source concepts language.\n\n## Accessing concept edges with a given relation direction\n\nYou can also query the relations that have a specific concept as target or source. This is achieved with `concept.edges_out` and `concept.edges_in`, as follows:\n\n```python\nfrom conceptnet_lite import Language, Label\n\nenglish = Language.get(name=\'en\')\ncat_concepts = Label.get(text=\'introvert\', language=english).concepts  #\nfor c in cat_concepts:\n    print("    Concept text:", c.text)\n    if c.edges_out:\n        print("      Edges out:")\n        for e in c.edges_out:\n            print("        Edge URI:", e.uri)\n            print("        Relation:", e.relation.name)\n            print("        End:", e.end.text)\n    if c.edges_in:\n        print("      Edges in:")\n        for e in c.edges_in:\n            print("        Edge URI:", e.uri)\n            print("        Relation:", e.relation.name)\n            print("        End:", e.end.text)\n```\n\n\n# Traversing all the data for a language\n\nYou can go over all concepts for a given language. For illustration, let us try Avestan, a "small" language with the code "ae" and vocab size of 371, according to the [ConceptNet language statistics](https://github.com/commonsense/conceptnet5/wiki/Languages).\n\n```python\nfrom conceptnet_lite import Language\n\nmylanguage = Language.get(name=\'ae\')\nfor l in mylanguage.labels:\n    print("  Label:", l.text)\n    for c in l.concepts:\n        print("    Concept URI:", c.uri)\n        if c.edges_out:\n            print("      Edges out:")\n            for e in c.edges_out:\n                print("        Edge URI:", e.uri)\n        if c.edges_in:\n            print("      Edges in:")\n            for e in c.edges_in:\n                print("        Edge URI:", e.uri)\n```\n\nTodo:\n\n- [ ] add database file link\n- [ ] describe how to build the database\n- [ ] add sample outputs\n',
    'author': 'Roman Inflianskas',
    'author_email': 'infroma@gmail.com',
    'url': 'https://github.com/ldtoolkit/conceptnet-lite',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
