import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from crystal_toolkit import GraphComponent
from crystal_toolkit.components.core import MPComponent, PanelComponent
from crystal_toolkit.helpers.layouts import *
from crystal_toolkit.components.structure import StructureMoleculeComponent

from pymatgen.core.structure import Structure, Molecule
from pymatgen.analysis.graphs import StructureGraph, MoleculeGraph

from typing import Union


class BondingGraphComponent(PanelComponent):
    @property
    def title(self):
        return "Bonding and Local Environments"

    @property
    def description(self):
        return (
            "See an abstract 2D representation of the bonding in this "
            "structure and different local environments."
        )

    @staticmethod
    def get_graph_data(
        graph: Union[StructureGraph, MoleculeGraph],
        color_scheme="Jmol",
        color_scale=None,
    ):

        nodes = []
        edges = []

        struct_or_mol = StructureMoleculeComponent._get_struct_or_mol(graph)
        site_prop_types = StructureMoleculeComponent._analyze_site_props(struct_or_mol)
        colors, _ = StructureMoleculeComponent._get_display_colors_and_legend_for_sites(
            struct_or_mol,
            site_prop_types,
            color_scheme=color_scheme,
            color_scale=color_scale,
        )

        for node in graph.graph.nodes():

            nodes.append({"id": node, "title": f"{struct_or_mol[node].species_string} site", "color": colors[node][0]})

        for u, v, d in graph.graph.edges(data=True):

            edge = {"from": u, "to": v, "arrows": ""}

            to_jimage = d.get("to_jimage", (0, 0, 0))

            # TODO: check these edge weights
            if isinstance(struct_or_mol, Structure):
                dist = struct_or_mol.get_distance(u, v, jimage=to_jimage)
            else:
                dist = struct_or_mol.get_distance(u, v)
            edge["length"] = 50 * dist

            label = f"{dist:.2f} Å bond"
            # if 'weight' in d:
            #    label += f" {d['weight']}"
            if to_jimage != (0, 0, 0):
                edge["arrows"] = "to"
                label += f" to site at image vector {to_jimage}"

            if label:
                edge["title"] = label

            edges.append(edge)

        return {"nodes": nodes, "edges": edges}

    def update_contents(self, new_store_contents):

        if not new_store_contents:
            raise PreventUpdate

        graph = self.from_data(new_store_contents)
        graph_data = self.get_graph_data(graph)

        options = {"interaction": {"hover": True}}

        return html.Div(
            [GraphComponent(graph=graph_data, options=options)],
            style={"width": "65vmin", "height": "65vmin"},
        )