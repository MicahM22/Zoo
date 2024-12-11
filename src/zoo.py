from os.path import dirname, join
from textx import metamodel_from_file
from textx.export import metamodel_export, model_export
import tkinter as tk
from tkinter import PhotoImage
from graphviz import Digraph
import os
import requests
import wikipediaapi
import textwrap

def split_sentences(paragraph):
    delimiters = ".?!"
    sentences = []
    sentence = ""
    for char in paragraph:
        sentence += char
        if char in delimiters:
            sentences.append(sentence.strip())
            sentence = ""
    if sentence:
        sentences.append(sentence.strip())
    return sentences

def get_image_url(query):
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"File:{query}",
        "gsrlimit": 1,
        "prop": "imageinfo",
        "iiprop": "url"
    }
    
    response = requests.get(url, params=params)
    data = response.json()

    try:
        pages = data["query"]["pages"]
        for _, page in pages.items():
            if "imageinfo" in page:
                return page["imageinfo"][0]["url"]
    except KeyError:
        return None

def find_section_by_keyword(page, keyword):
    # Recursive function to search for a section containing the keyword
    def search_sections(sections, keyword):
        for section in sections:
            if keyword in section.title.lower():  # Case-insensitive match
                return section
            # Recursively search subsections
            found = search_sections(section.sections, keyword)
            if found:
                return found
        return None

    return search_sections(page.sections, keyword)


def generate_tree(model):
    dot = Digraph()
    dot.attr(
        dpi="70",
        size="40,10",
        center="true",
        rankdir="TB",
        margin="10,5",
        outputorder="edgesfirst"       
    )

    dot.attr(nodesep="0.5", ranksep="0.8")
    dot.attr(ratio="fill") 
    



  
  

    for kingdom in model.kingdoms:
        kingdom_color = str(kingdom.color) if kingdom.color else "#000000"
        dot.node(kingdom.name, f"Kingdom: {kingdom.name}", color=kingdom_color)

        for phylum in kingdom.phyla:
            phylum_color = str(phylum.color) if phylum.color else "#000000"
            dot.node(phylum.name, f"Phylum: {phylum.name}", color=phylum_color)
            dot.edge(kingdom.name, phylum.name)

            for _class in phylum.classes:
                class_color = str(_class.color) if _class.color else "#000000"
                dot.node(_class.name, f"Class: {_class.name}", color=class_color)
                dot.edge(phylum.name, _class.name)

                for order in _class.orders:
                    order_color = str(order.color) if order.color else "#000000"
                    dot.node(order.name, f"Order: {order.name}", color=order_color)
                    dot.edge(_class.name, order.name)

                    for family in order.families:
                        family_color = str(family.color) if family.color else "#000000"
                        dot.node(family.name, f"Family: {family.name}", color=family_color)
                        dot.edge(order.name, family.name)

                        if family.subfamilies:
                            for subfamily in family.subfamilies:
                                subfamily_color = str(subfamily.color) if subfamily.color else "#000000"
                                dot.node(subfamily.name, f"Subfamily: {subfamily.name}", color=subfamily_color)
                                dot.edge(family.name, subfamily.name)

                                for genus in subfamily.genera:
                                    genus_color = str(genus.color) if genus.color else "#000000"
                                    dot.node(genus.name, f"Genus: {genus.name}", color=genus_color)
                                    dot.edge(subfamily.name, genus.name)

                                    for species in genus.species:
                                        species_color = str(species.color) if species.color else "#000000"
                                        species_name = f"{species.parent.name} {species.name}"
                                        species_commonName = species.common_name if species.common_name else 'N/A'
                                        species_synonym = species.synonym if species.synonym else 'N/A'
                                        if species.common_name:
                                            wiki_wiki = wikipediaapi.Wikipedia("Zoo Project")
                                            page_py = wiki_wiki.page(species_commonName)
                                            section_history = find_section_by_keyword(page_py, "taxonomy")
                                            if section_history and species.taxonomy:
                                                taxonomy = (section_history.text)
                                                taxonomy_sentences = split_sentences(taxonomy)
                                                first_three_sentences = " ".join(taxonomy_sentences[:3])
                                                wrapped_taxonomy = textwrap.fill(first_three_sentences, width=40)
                                                dot.node(species.name, label=f"Species: {species.name}\nCommon Name: {species_commonName}\nSynonym: {species_synonym}\nTaxonomy: {wrapped_taxonomy}", URL = get_image_url(species_name), color=species_color, shape="rect")
                                            else: 
                                                dot.node(species.name,  label=f"Species: {species.name}\nCommon Name: {species_commonName}\nSynonym: {species_synonym}", URL = get_image_url(species_name), color=species_color, shape="rect")
                                    dot.edge(genus.name, species.name)

                        else:
                            for genus in family.genera:
                                genus_color = str(genus.color) if genus.color else "#000000"
                                dot.node(genus.name, f"Genus: {genus.name}", color=genus_color)
                                dot.edge(family.name, genus.name)

                                for species in genus.species:
                                    species_color = str(species.color) if species.color else "#000000"
                                    species_name = f"{species.parent.name} {species.name}"
                                    species_commonName = species.common_name if species.common_name else 'N/A'
                                    species_synonym = species.synonym if species.synonym else 'N/A'
                                    if species.common_name:
                                            wiki_wiki = wikipediaapi.Wikipedia("Zoo Project")
                                            page_py = wiki_wiki.page(species_commonName)
                                            section_history = find_section_by_keyword(page_py, "taxonomy")
                                            if section_history and species.taxonomy:
                                                taxonomy = (section_history.text)
                                                taxonomy_sentences = split_sentences(taxonomy)
                                                first_three_sentences = " ".join(taxonomy_sentences[:3])
                                                wrapped_taxonomy = textwrap.fill(first_three_sentences, width=40)
                                                dot.node(species.name, label=f"Species: {species.name}\nCommon Name: {species_commonName}\nSynonym: {species_synonym}\nTaxonomy: {wrapped_taxonomy}", URL = get_image_url(species_name), color=species_color, shape="rect")
                                            else: 
                                                dot.node(species.name,  label=f"Species: {species.name}\nCommon Name: {species_commonName}\nSynonym: {species_synonym}", URL = get_image_url(species_name), color=species_color, shape="rect")
                                    dot.edge(genus.name, species.name)
                                    


  
    output_path = "Taxonomy_tree"
    dot.render('graph_output', format='svg', view=True)
    return output_path + ".svg"
file_path = r"C:\Users\micah\Zoo\graph_output.svg"




with open(file_path, "r") as file:
    data = file.read()
    data = "<!-- Test line added -->\n" + data


with open(file_path, "w") as file:
    file.write(data)




if __name__ == "__main__":
    this_folder = dirname(__file__)

    zoo_mm = metamodel_from_file(join(this_folder, 'zoo.tx'), debug=False)
    metamodel_export(zoo_mm, join(this_folder, 'zoo_meta.dot'))

    zoo_model = zoo_mm.model_from_file(join(this_folder, 'program.zoo'))
    model_export(zoo_model, join(this_folder, 'program.dot'))

    tree_image = generate_tree(zoo_model)
   
