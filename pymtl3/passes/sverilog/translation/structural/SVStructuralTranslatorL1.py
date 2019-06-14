#=========================================================================
# SVStructuralTranslatorL1.py
#=========================================================================
"""Provide SystemVerilog structural translator implementation."""

from __future__ import absolute_import, division, print_function

from functools import reduce

from pymtl3.datatypes import Bits
from pymtl3.passes.rtlir import RTLIRDataType as rdt
from pymtl3.passes.sverilog.errors import SVerilogReservedKeywordError
from pymtl3.passes.sverilog.util.utility import get_component_unique_name, make_indent
from pymtl3.passes.translator.structural.StructuralTranslatorL1 import (
    StructuralTranslatorL1,
)


class SVStructuralTranslatorL1( StructuralTranslatorL1 ):

  def check_decl( s, name, msg ):
    if s.is_sverilog_reserved( name ):
      raise SVerilogReservedKeywordError( name, msg )

  #-----------------------------------------------------------------------
  # Data types
  #-----------------------------------------------------------------------

  def rtlir_tr_vector_dtype( s, dtype ):
    msb = dtype.get_length() - 1
    return {
      'def'  : '',
      'nbits' : dtype.get_length(),
      'const_decl' : '[{msb}:0] {{id_}}'.format( **locals() ),
      'decl' : 'logic [{msb}:0] {{id_}}'.format( **locals() ),
      'raw_dtype' : dtype
    }

  def rtlir_tr_unpacked_array_type( s, Type ):
    if Type is None:
      return { 'def' : '', 'decl' : '', 'n_dim':[] }
    else:
      array_dim = reduce(
        lambda x,y: x+'[0:{}]'.format(y-1), Type.get_dim_sizes(), '' )
      return {
        'def'  : '',
        'decl' : ' ' + array_dim,
        'n_dim' : Type.get_dim_sizes()
      }

  #-----------------------------------------------------------------------
  # Declarations
  #-----------------------------------------------------------------------
  
  def rtlir_tr_port_decls( s, port_decls ):
    make_indent( port_decls, 1 )
    return ',\n'.join( port_decls )
  
  def rtlir_tr_port_decl( s, id_, Type, array_type, dtype ):
    _dtype = Type.get_dtype()
    if array_type:
      template = "Note: port {id_} has data type {_dtype}"
    else:
      n_dim = array_type['n_dim']
      template = "Note: {n_dim} array of ports {id_} has data type {_dtype}"
    s.check_decl( id_, template.format( **locals() ) )
    return Type.get_direction() + ' ' + \
           dtype['decl'].format( **locals() ) + array_type['decl']
  
  def rtlir_tr_wire_decls( s, wire_decls ):
    make_indent( wire_decls, 1 )
    return '\n'.join( wire_decls )
  
  def rtlir_tr_wire_decl( s, id_, Type, array_type, dtype ):
    _dtype = Type.get_dtype()
    if array_type:
      template = "Note: wire {id_} has data type {_dtype}"
    else:
      n_dim = array_type['n_dim']
      template = "Note: {n_dim} array of wires {id_} has data type {_dtype}"
    s.check_decl( id_, template.format( **locals() ) )
    return dtype['decl'].format( **locals() ) + array_type['decl'] + ';'
  
  def rtlir_tr_const_decls( s, const_decls ):
    make_indent( const_decls, 1 )
    return '\n'.join( const_decls )
  
  def rtlir_tr_const_decl( s, id_, Type, array_type, dtype, value ):

    def gen_array_param( n_dim, array ):
      if not n_dim:
        assert not isinstance( array, list )
        if isinstance( array, Bits ):
          return s._literal_number( array.nbits, array.value )
        elif isinstance( array, int ):
          return s._literal_number( 32, array )
        else:
          assert False, '{} is not an integer!'.format( array )
      assert isinstance( array, list )

      ret = "'{ "
      for _idx, idx in enumerate( range( n_dim[0] ) ):
        if _idx != 0: ret += ', '
        ret += gen_array_param( n_dim[1:], array[idx] )
      ret += " }"
      return ret

    assert isinstance( Type.get_dtype(), rdt.Vector ), \
      '{} is not a vector constant!'.format( value )

    _dtype = Type.get_dtype()
    if array_type:
      template = "Note: constant {id_} has data type {_dtype}"
    else:
      n_dim = array_type['n_dim']
      template = "Note: {n_dim} array of constants {id_} has data type {_dtype}"
    s.check_decl( id_, template.format( **locals() ) )

    nbits = dtype['nbits']
    _dtype = dtype['const_decl'].format( **locals() ) + array_type['decl']
    _value = gen_array_param( array_type['n_dim'], value )

    return 'localparam {_dtype} = {_value};'.format( **locals() )

  #-----------------------------------------------------------------------
  # Connections
  #-----------------------------------------------------------------------
  
  def rtlir_tr_connections( s, connections ):
    make_indent( connections, 1 )
    return '\n'.join( connections )
  
  def rtlir_tr_connection( s, wr_signal, rd_signal ):
    return 'assign {rd_signal} = {wr_signal};'.format( **locals() )

  #-----------------------------------------------------------------------
  # Signal operations
  #-----------------------------------------------------------------------
  
  def rtlir_tr_bit_selection( s, base_signal, index ):
    # Bit selection
    return '{base_signal}[{index}]'.format( **locals() )

  def rtlir_tr_part_selection( s, base_signal, start, stop ):
    # Part selection
    _stop = stop-1
    return '{base_signal}[{_stop}:{start}]'.format( **locals() )

  def rtlir_tr_port_array_index( s, base_signal, index ):
    return '{base_signal}[{index}]'.format( **locals() )

  def rtlir_tr_wire_array_index( s, base_signal, index ):
    return '{base_signal}[{index}]'.format( **locals() )

  def rtlir_tr_const_array_index( s, base_signal, index ):
    return '{base_signal}[{index}]'.format( **locals() )

  def rtlir_tr_current_comp_attr( s, base_signal, attr ):
    return '{attr}'.format( **locals() )

  def rtlir_tr_current_comp( s, comp_id, comp_rtype ):
    return ''

  #-----------------------------------------------------------------------
  # Miscs
  #-----------------------------------------------------------------------

  def rtlir_tr_var_id( s, var_id ):
    return var_id.replace( '[', '_$' ).replace( ']', '' )

  def _literal_number( s, nbits, value ):
    value = int( value )
    return "{nbits}'d{value}".format( **locals() )

  def rtlir_tr_literal_number( s, nbits, value ):
    return s._literal_number( nbits, value )

  def rtlir_tr_component_unique_name( s, c_rtype ):
    return get_component_unique_name( c_rtype )
