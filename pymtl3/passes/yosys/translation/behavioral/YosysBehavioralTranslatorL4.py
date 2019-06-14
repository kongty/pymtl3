#=========================================================================
# YosysBehavioralTranslatorL4.py
#=========================================================================
# Author : Peitian Pan
# Date   : June 9, 2019
"""Provide the yosys-compatible SystemVerilog L4 behavioral translator."""

from __future__ import absolute_import, division, print_function

from pymtl3.passes.rtlir import RTLIRType as rt
from pymtl3.passes.sverilog.translation.behavioral.SVBehavioralTranslatorL4 import (
    BehavioralRTLIRToSVVisitorL4,
    SVBehavioralTranslatorL4,
)

from .YosysBehavioralTranslatorL3 import (
    YosysBehavioralRTLIRToSVVisitorL3,
    YosysBehavioralTranslatorL3,
)


class YosysBehavioralTranslatorL4(
    YosysBehavioralTranslatorL3, SVBehavioralTranslatorL4 ):

  def _get_rtlir2sv_visitor( s ):
    return YosysBehavioralRTLIRToSVVisitorL4

class YosysBehavioralRTLIRToSVVisitorL4(
    YosysBehavioralRTLIRToSVVisitorL3, BehavioralRTLIRToSVVisitorL4 ):

  def visit_Attribute( s, node ):
    """Return the SystemVerilog representation of an attribute.
    
    Add support for accessing interface attribute in L4.
    """
    # import pdb
    # pdb.set_trace()
    if isinstance( node.value.Type, rt.InterfaceView ):
      value = s.visit( node.value )
      s.signal_expr_prologue( node )
      attr = node.attr
      s.check_res( node, attr )
      node.sexpr['s_attr'] += "${}"
      node.sexpr['attr'].append( attr )
      return s.signal_expr_epilogue(node, "{value}.{attr}".format(**locals()))

    else:
      return super( YosysBehavioralRTLIRToSVVisitorL4, s ).visit_Attribute( node )
