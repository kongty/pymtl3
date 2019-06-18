#=========================================================================
# YosysTranslator.py
#=========================================================================
# Author : Peitian Pan
# Date   : June 8, 2019
"""Provide yosys-compatible SystemVerilog translator."""

from __future__ import absolute_import, division, print_function

from pymtl3.passes.sverilog.translation.SVTranslator import mk_SVTranslator
from pymtl3.passes.translator import RTLIRTranslator

from .behavioral import YosysBehavioralTranslator as Yosys_BTranslator
from .structural import YosysStructuralTranslator as Yosys_STranslator

SVTranslator = mk_SVTranslator( RTLIRTranslator, Yosys_STranslator, Yosys_BTranslator )

class YosysTranslator( SVTranslator ):

  def set_header( s ):
      s.header = \
"""\
//-------------------------------------------------------------------------
// {name}.sv
//-------------------------------------------------------------------------
// This file is generated by PyMTL yosys-SystemVerilog translation pass.

"""

  def rtlir_tr_src_layout( s, hierarchy ):
    s.set_header()
    name = s._top_module_full_name
    ret = s.header.format( **locals() )

    # Add component sources
    ret += hierarchy.component_src
    return ret

  def rtlir_tr_component( s, behavioral, structural ):

    template =\
"""\
// Definition of PyMTL Component {component_name}
// {file_info}
module {module_name}
(
{ports});
{body}
endmodule
"""
    component_name = getattr( structural, "component_name" )
    file_info = getattr( structural, "component_file_info" )
    ports_template = "{port_decls}{ifc_decls}"
    module_name = getattr( structural, "component_unique_name" )

    port_dct = getattr( structural, "decl_ports" )
    structural.p_port_decls = port_dct["port_decls"]
    structural.p_wire_decls = port_dct["wire_decls"]
    structural.p_connections = port_dct["connections"]

    ifc_dct = getattr( structural, "decl_ifcs" )
    structural.i_port_decls = ifc_dct["port_decls"]
    structural.i_wire_decls = ifc_dct["wire_decls"]
    structural.i_connections = ifc_dct["connections"]

    subcomp_dct = getattr( structural, "decl_subcomps" )
    structural.c_port_decls = subcomp_dct["port_decls"]
    structural.c_wire_decls = subcomp_dct["wire_decls"]
    structural.c_connections = subcomp_dct["connections"]

    # Assemble ports and interfaces
    port_decls = s.get_pretty(structural, 'p_port_decls', False)
    ifc_decls = s.get_pretty(structural, 'i_port_decls', False)
    if port_decls or ifc_decls:
      if port_decls and ifc_decls:
        port_decls += ',\n'
      ifc_decls += '\n'
    ports = ports_template.format(**locals())

    # Assemble body of module definition
    p_port_wires = s.get_pretty(structural, "p_wire_decls", False)
    i_port_wires = s.get_pretty(structural, "i_wire_decls", False)

    if p_port_wires or i_port_wires:
      if p_port_wires and i_port_wires:
        p_port_wires += ",\n"
      i_port_wires += "\n"
    port_wires = p_port_wires + i_port_wires

    wire_decls = s.get_pretty(structural, "decl_wires")
    tmpvar_decls = s.get_pretty(behavioral, "decl_tmpvars")

    subcomp_wires = s.get_pretty(structural, "c_wire_decls")
    subcomp_ports = s.get_pretty(structural, "c_port_decls")
    subcomp_conns = s.get_pretty(structural, "c_connections")

    upblk_decls = s.get_pretty(behavioral, "upblk_decls")

    body = port_wires + wire_decls \
         + subcomp_wires + subcomp_ports + subcomp_conns \
         + tmpvar_decls + upblk_decls

    # Assemble connections
    p_conns = s.get_pretty(structural, "p_connections", False)
    i_conns = s.get_pretty(structural, "i_connections", False)

    if p_conns or i_conns:
      if p_conns and i_conns:
        p_conns += ",\n"
      i_conns += "\n"
    port_connections = p_conns + i_conns
    connections = port_connections \
                + s.get_pretty(structural, "connections")
    if (body and connections) or (not body and connections):
      connections = '\n' + connections
    body += connections

    s._top_module_name = getattr( structural, "component_name", module_name )
    s._top_module_full_name = module_name
    return template.format( **locals() )