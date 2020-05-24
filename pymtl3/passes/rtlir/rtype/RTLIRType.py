#=========================================================================
# RTLIRType.py
#=========================================================================
# Author : Peitian Pan
# Date   : March 31, 2019
"""RTLIR instance types and generation methods.

This file contains the definitions of RTLIR instance types and methods
that generate RTLIR instances. Each instance of the non-abstract class
listed in this module is a type instance or simply a type in the RTLIR
type system. Signal types is parameterized by data types defined in the
RTLIR data type module.
"""
import copy
import inspect
import math

import pymtl3.dsl as dsl
from pymtl3.datatypes import Bits, is_bitstruct_inst

from ..errors import RTLIRConversionError
from ..util.utility import collect_objs
from .RTLIRDataType import BaseRTLIRDataType, PackedArray, get_rtlir_dtype


class BaseRTLIRType:
  """Base abstract class for all RTLIR instance types."""
  def __ne__( s, other ):
    return not s.__eq__( other )

class NoneType( BaseRTLIRType ):
  """Type for not yet typed RTLIR temporary variables."""
  def __eq__( s, other ):
    return isinstance( other, NoneType )

  def __hash__( s ):
    return hash(type(s))

  def __str__( s ):
    return 'NoneType'

  def __repr__( s ):
    return 'NoneType'

class Array( BaseRTLIRType ):
  """Unpacked RTLIR array type."""
  def __init__( s, dim_sizes, sub_type, obj = None, unpacked = False ):
    assert isinstance( sub_type, BaseRTLIRType ), \
      f"array subtype {sub_type} is not RTLIR type!"
    assert not isinstance( sub_type, Array ), \
      f"array subtype {sub_type} should not be array RTLIR type!"
    assert len( dim_sizes ) >= 1, "array should be non-empty!"
    assert sum( dim_sizes ) > 0, "array should have at least one element!"
    s.dim_sizes = dim_sizes
    s.sub_type = sub_type
    s.unpacked = unpacked
    s.obj = obj

  def _is_unpacked( s ):
    return s.unpacked

  def __eq__( s, other ):
    if not isinstance( other, Array ): return False
    if s.dim_sizes != other.dim_sizes: return False
    return s.sub_type == other.sub_type

  def __hash__( s ):
    return hash((type(s), tuple(s.dim_sizes), s.sub_type))

  def get_obj( s ):
    return s.obj

  def get_next_dim_type( s ):
    if len( s.dim_sizes ) == 1: return copy.copy( s.sub_type )
    _s = copy.copy( s )
    _s.dim_sizes = s.dim_sizes[1:]
    return _s

  def get_dim_sizes( s ):
    return s.dim_sizes

  def get_index_width( s ):
    assert s.dim_sizes, 'rt.Array is created without dimension!'
    n_elements = s.dim_sizes[0]
    if n_elements <= 1:
      return 1
    else:
      return math.ceil(math.log2(n_elements))

  def get_sub_type( s ):
    return s.sub_type

  def __call__( s, obj ):
    """Return if obj be cast into type `s`."""
    return s == obj

  def __str__( s ):
    return 'Array'

  def __repr__( s ):
    return f'Array{s.dim_sizes} of {s.sub_type}'

class Signal( BaseRTLIRType ):
  """Signal abstract RTLIR instance type.

  A Signal can be a Port, a Wire, or a Const.
  """
  def __init__( s, dtype, unpacked = False ):
    assert isinstance( dtype, BaseRTLIRDataType ), \
      f"signal parameterized by non-RTLIR data type {dtype}!"
    s.dtype = dtype
    s.unpacked = unpacked

  def __hash__( s ):
    return hash((type(s), s.dtype))

  def is_packed_indexable( s ):
    return isinstance( s.dtype, PackedArray )

  def get_dtype( s ):
    return s.dtype

  def get_index_width( s ):
    return s.dtype.get_index_width()

  def _is_unpacked( s ):
    return s.unpacked

class Port( Signal ):
  """Port RTLIR instance type."""
  def __init__( s, direction, dtype, unpacked = False ):
    super().__init__( dtype, unpacked )
    s.direction = direction

  def __eq__( s, other ):
    return isinstance(other, Port) and s.dtype == other.dtype and \
           s.direction == other.direction

  def __hash__( s ):
    return hash((type(s), s.dtype, s.direction))

  def __str__( s ):
    return 'Port'

  def __repr__( s ):
    return f'Port of {s.dtype}'

  def get_direction( s ):
    return s.direction

  def get_next_dim_type( s ):
    assert s.is_packed_indexable(), "cannot index on unindexable port!"
    return Port( s.direction, s.dtype.get_next_dim_type(), s.unpacked )

class Wire( Signal ):
  """Wire RTLIR instance type."""
  def __init__( s, dtype, unpacked = False ):
    super().__init__( dtype, unpacked )

  def __eq__( s, other ):
    return isinstance(other, Wire) and s.dtype == other.dtype

  def __hash__( s ):
    return hash((type(s), s.dtype))

  def __str__( s ):
    return 'Wire'

  def __repr__( s ):
    return f'Wire of {s.dtype}'

  def get_next_dim_type( s ):
    assert s.is_packed_indexable(), "cannot index on unindexable wire!"
    return Wire( s.dtype.get_next_dim_type(), s.unpacked )

class NetWire( Signal ):
  """NetWire RTLIR instance type.

  Objects of this class are generated by the behavioral RTLIR type check pass
  to mark an expression as not available for any signal operations ( i.e.
  bit selection, part selection, attribute access ). This is useful because
  some backend tools ( like verilator ) does not support indexing/slicing over
  an already indexed/sliced signal ( the "net wire" ).
  """
  def __init__( s, dtype, unpacked = False ):
    super().__init__( dtype, unpacked )

  def __eq__( s, other ):
    return isinstance(other, NetWire) and s.dtype == other.dtype

  def __hash__( s ):
    return hash((type(s), s.dtype))

  def __str__( s ):
    return 'NetWire'

  def __repr__( s ):
    return f'NetWire of {s.dtype}'

  def get_next_dim_type( s ):
    assert s.is_packed_indexable(), "cannot index on unindexable net wire!"
    return NetWire( s.dtype.get_next_dim_type(), s.unpacked )

class Const( Signal ):
  """Const RTLIR instance type."""
  def __init__( s, dtype, obj = None, unpacked = False ):
    super().__init__( dtype, unpacked )
    s.obj = obj

  def __eq__( s, other ):
    return isinstance(other, Const) and s.dtype == other.dtype

  def __hash__( s ):
    return hash((type(s), s.dtype))

  def __str__( s ):
    return 'Const'

  def __repr__( s ):
    return f'Const of {s.dtype}'

  def get_object( s ):
    return s.obj

  def get_next_dim_type( s ):
    assert s.is_packed_indexable(), "cannot index on unindexable constant!"
    return Const( s.dtype.get_next_dim_type(), s.unpacked )

class InterfaceView( BaseRTLIRType ):
  """RTLIR instance type for a view of an interface."""
  def __init__( s, name, properties, obj = None, unpacked = False ):
    s.name = name
    s.properties = properties
    s.obj = obj
    s.cls = obj.__class__
    s.unpacked = unpacked

    if obj is not None:
      try:
        s.args = obj._dsl.args
        s.kwargs = obj._dsl.kwargs
      except AttributeError:
        assert False, f"interface object {s.obj} is not constructed!"

    # Sanity check
    for name, rtype in properties.items():
      assert isinstance(name, str) and _is_of_type(rtype, (Port, InterfaceView)), \
        f"invalid attribute {name} of interface {s.name}: only ports and interfaces allowed!"

  def __str__( s ):
    return f'InterfaceView {s.name}'

  def __repr__( s ):
    return f'InterfaceView {s.name}'

  def _is_unpacked( s ):
    return s.unpacked

  def __eq__( s, other ):
    return isinstance(other, InterfaceView) and s.name == other.name

  def __hash__( s ):
    return hash((type(s), s.name))

  def get_name( s ):
    return s.name

  def get_class( s ):
    return s.cls

  def get_args( s ):
    if s.obj is not None:
      return ( s.args, s.kwargs )
    else:
      return ( [], {} )

  def get_input_ports( s ):
    return sorted([id__port for id__port in s.properties.items() if id__port[1].direction == 'input'], key = lambda kv: kv[0])

  def get_output_ports( s ):
    return sorted([id__port1 for id__port1 in s.properties.items() if id__port1[1].direction == 'output'], key = lambda kv: kv[0])

  def has_property( s, p ):
    return p in s.properties

  def get_property( s, p ):
    return s.properties[ p ]

  def get_all_ports( s ):
    return sorted([name_port for name_port in s.properties.items() if isinstance( name_port[1], Port )], key = lambda kv: kv[0])

  def get_all_ports_packed( s ):
    return sorted([id__t2 for id__t2 in s.properties.items() if ( isinstance( id__t2[1], Port ) and not id__t2[1]._is_unpacked() ) or \
        ( isinstance( id__t2[1], Array ) and isinstance( id__t2[1].get_sub_type(), Port ) \
          and not id__t2[1]._is_unpacked() )], key = lambda kv: kv[0])

  def get_all_properties( s ):
    return sorted( s.properties.items(), lambda kv: kv[0] )

  def get_all_properties_packed( s ):
    return sorted( [x for x in s.properties.items() if not x[1]._is_unpacked()],
        key = lambda kv: kv[0] )

class Component( BaseRTLIRType ):
  """RTLIR instance type for a component."""
  def __init__( s, obj, properties, unpacked = False ):
    s.name = obj.__class__.__name__
    s.params = s._gen_parameters( obj )
    s.properties = properties
    s.unpacked = unpacked
    s.obj = obj
    cls = obj.__class__
    try:
      file_name = inspect.getsourcefile( cls )
      s.file_info = f"{file_name}"
      # line_no = inspect.getsourcelines( cls )[1]
      # s.file_info = f"{file_name}:{line_no}"
    except OSError:
      s.file_info = f"Dynamically generated component {cls.__name__}"

  def _gen_parameters( s, obj ):
    # s.argspec: static code reflection results
    # _dsl.args: all unnamed arguments supplied to construct()
    # _dsl.kwargs: all named arguments supplied to construct()
    try:
      argspec = inspect.getfullargspec( obj.construct )
      assert not argspec.varkw, "keyword args are not allowed for construct!"
      assert not argspec.kwonlyargs, "keyword args are not allowed for construct!"
    except AttributeError:
      argspec = inspect.getargspec( obj.construct )
      assert not argspec.keywords, "keyword args are not allowed for construct!"
    assert not argspec.varargs, "varargs are not allowed for construct!"
    arg_names = argspec.args[1:]

    defaults = argspec.defaults or ()
    num_args = len(arg_names)
    num_supplied = len(obj._dsl.args) + len(obj._dsl.kwargs)
    num_defaults = len(defaults)

    # No default values: each arg is either keyword or unnamed
    # Has default values: num. supplied values + num. of defaults >= num. args
    assert num_args == num_supplied or num_args <= num_supplied + num_defaults, \
        "internal error: fail to parse the arguments!"
    use_defaults = num_args != num_supplied

    ret = []
    # Handle method construct arguments
    for idx, arg_name in enumerate(arg_names):

      # Use values from _dsl.args
      if idx < len(obj._dsl.args):
        ret.append((arg_name, obj._dsl.args[idx]))

      # Use values from _dsl.kwargs
      elif arg_name in obj._dsl.kwargs:
        ret.append((arg_name, obj._dsl.kwargs[arg_name]))

      # Use default values
      else:
        assert use_defaults, "internal error: didn't expect to use default values!"
        ret.append((arg_name, defaults[idx-len(arg_names)]))

    return ret

  def _is_unpacked( s ):
    return s.unpacked

  def _has_same_interface( s, other ):
    u, v = s.get_ports_packed(), other.get_ports_packed()
    return (len(u)==len(v)) and all(_u == _v for _u, _v in zip(u, v))

  def __eq__( s, other ):
    # Two Components are considered equal iff they expose the same interface
    return isinstance(other, Component) and s._has_same_interface( other )

  def __hash__( s ):
    return hash((type(s), s.name, tuple(s.params)))

  def __str__( s ):
    return f'Component {s.name}'

  def __repr__( s ):
    port_strs = ["{}:{}".format(name, repr(rtype)) for name, rtype in s.get_ports_packed()]
    return f'Component with interface: {", ".join(port_strs)}'

  def get_name( s ):
    return s.name

  def get_obj( s ):
    return s.obj

  def get_file_info( s ):
    return s.file_info

  def get_params( s ):
    return s.params

  def get_ports( s ):
    return sorted([id__port3 for id__port3 in s.properties.items() if isinstance( id__port3[1], Port )], key = lambda kv: kv[0])

  def get_ports_packed( s ):
    return sorted([id__t4 for id__t4 in s.properties.items() if ( isinstance( id__t4[1], Port ) and not id__t4[1]._is_unpacked() ) or \
        ( isinstance( id__t4[1], Array ) and isinstance( id__t4[1].get_sub_type(), Port ) \
          and not id__t4[1]._is_unpacked() )], key = lambda kv: kv[0])

  def get_wires( s ):
    return sorted([id__wire for id__wire in s.properties.items() if isinstance( id__wire[1], Wire )], key = lambda kv: kv[0])

  def get_wires_packed( s ):
    return sorted([id__t5 for id__t5 in s.properties.items() if ( isinstance( id__t5[1], Wire ) and not id__t5[1]._is_unpacked() ) or \
        ( isinstance( id__t5[1], Array ) and isinstance( id__t5[1].get_sub_type(), Wire ) \
          and not id__t5[1]._is_unpacked() )], key = lambda kv: kv[0])

  def get_consts( s ):
    return sorted([id__const for id__const in s.properties.items() if isinstance( id__const[1], Const )], key = lambda kv: kv[0])

  def get_consts_packed( s ):
    return sorted([id__t6 for id__t6 in s.properties.items() if ( isinstance( id__t6[1], Const ) and not id__t6[1]._is_unpacked() ) or \
        ( isinstance( id__t6[1], Array ) and isinstance( id__t6[1].get_sub_type(), Const ) \
          and not id__t6[1]._is_unpacked() )], key = lambda kv: kv[0])

  def get_ifc_views( s ):
    return sorted([id__ifc for id__ifc in s.properties.items() if isinstance( id__ifc[1], InterfaceView )], key = lambda kv: kv[0])

  def get_ifc_views_packed( s ):
    return sorted([id__t7 for id__t7 in s.properties.items() if ( isinstance( id__t7[1], InterfaceView ) and not id__t7[1]._is_unpacked() ) or \
        ( isinstance( id__t7[1], Array ) and isinstance( id__t7[1].get_sub_type(),InterfaceView ) \
          and not id__t7[1]._is_unpacked() )], key = lambda kv: kv[0])

  def get_subcomps( s ):
    return sorted([id__subcomp for id__subcomp in s.properties.items() if isinstance( id__subcomp[1], Component )], key = lambda kv: kv[0])

  def get_subcomps_packed( s ):
    return sorted([id__t9 for id__t9 in s.properties.items() if ( isinstance( id__t9[1], Component ) and not id__t9[1]._is_unpacked() ) or \
        ( isinstance( id__t9[1], Array ) and isinstance( id__t9[1].get_sub_type(), Component ) \
          and not id__t9[1]._is_unpacked() )], key = lambda kv: kv[0])

  def has_property( s, p ):
    return p in s.properties

  def get_property( s, p ):
    return s.properties[ p ]

  def get_all_properties( s ):
    return s.properties

#-------------------------------------------------------------------------
# Internal Methods
#-------------------------------------------------------------------------

def _is_rtlir_ifc_convertible( obj ):
  valid_ifc_attributes = ( dsl.InPort, dsl.OutPort, dsl.Interface )
  if isinstance( obj, list ):
    while isinstance( obj, list ):
      # Empty lists will be dropped
      if len( obj ) == 0:
        return True
      # assert len( obj ) > 0, f"one dimension of {obj} is 0!"
      obj = obj[0]
    return _is_rtlir_ifc_convertible( obj )
  elif isinstance( obj, valid_ifc_attributes ):
    return True
  else:
    return False

def _freeze( obj ):
  if isinstance( obj, list ):
    return tuple( _freeze(value) for value in obj )
  else:
    return obj

def _unpack( id_, Type ):
  if not isinstance( Type, Array ): return [ ( id_, Type ) ]
  ret = []
  for idx in range( Type.get_dim_sizes()[0] ):
    ret.append( ( f'{id_}[{idx}]', Type.get_next_dim_type() ) )
    ret.extend(_unpack(f'{id_}[{idx}]', Type.get_next_dim_type()))
  return ret

def _add_packed_instances( id_, Type, properties ):
  assert isinstance( Type, Array ), f"{Type} is not an array type!"
  for _id, _Type in _unpack( id_, Type ):
    assert hasattr( _Type, 'unpacked' ), f"{_Type} {_id} is not unpacked!"
    _Type.unpacked = True
    properties[ _id ] = _Type

def _is_of_type( obj, Type ):
  """Return True is `obj` is of RTLIR type `Type`."""
  if isinstance( obj, Type ):
    return True
  if isinstance( obj, Array ) and isinstance( obj.get_sub_type(), Type ):
    return True
  return False

def is_rtlir_convertible( obj ):
  """Return if `obj` can be converted into an RTLIR instance."""
  pymtl_constructs = (
    dsl.InPort, dsl.OutPort, dsl.Wire,
    Bits, dsl.Interface, dsl.Component,
  )
  # TODO: improve this long list of isinstance check
  if isinstance( obj, list ):
    while isinstance( obj, list ):
      # Empty lists will be dropped
      if len( obj ) == 0:
        return True
      obj = obj[0]
    return is_rtlir_convertible( obj )
  elif isinstance( obj, pymtl_constructs ):
    return True
  elif is_bitstruct_inst(obj):
    return True
  elif isinstance( obj, int ):
    return True
  else:
    return False

# Shunning: implement RTLIRGetter for per-translation cache instead of
# a global cache that invalidates garbage collection

NA = "<N/A>"

# uncached=0
class RTLIRGetter:
  ifc_primitive_types = ( dsl.InPort, dsl.OutPort, dsl.Interface )

  def __init__( self, cache=True ):
    if cache:
      self._rtlir_cache = {}
      self.get_rtlir = self._get_rtlir_cached
      # self.cache_hit = 0
      # self.cache_miss = 0
    else:
      self.get_rtlir = self._get_rtlir_uncached

    self._RTLIR_ifc_handlers = [
      ( list,          self._handle_Array ),
      ( dsl.InPort,    self._handle_InPort ),
      ( dsl.OutPort,   self._handle_OutPort ),
      ( dsl.Interface, self._handle_Interface ),
    ]

    self._RTLIR_handlers = [
      ( list,          self._handle_Array ),
      ( dsl.InPort,    self._handle_InPort ),
      ( dsl.OutPort,   self._handle_OutPort ),
      ( dsl.Wire,      self._handle_Wire ),
      ( ( int, Bits ), self._handle_Const ),
      ( dsl.Interface, self._handle_Interface ),
      ( dsl.Component, self._handle_Component ),
    ]

  #-------------------------------------------------------------------------
  # Public APIs
  #-------------------------------------------------------------------------

  def get_component_ifc_rtlir( self, obj ):
    """Return the RTLIR of the interfaces of component `obj`."""

    def _is_interface( id_, obj ):
      _type = type(obj)
      if isinstance( obj, self.ifc_primitive_types ):
        return True
      if not isinstance( obj, list ):
        return False
      if len(obj) == 0:
        return False
      obj = obj[0]
      while isinstance( obj, list ):
        if len( obj ) == 0:
          return False
        obj = obj[0]
      return isinstance( obj, self.ifc_primitive_types )

    try:
      assert isinstance(obj, dsl.Component), \
        "the given object is not a PyMTL component!"
      properties = {}
      collected_objs = collect_objs( obj, object )
      for _id, _obj in collected_objs:
        if _is_interface( _id, _obj ):
          for Type, handler in self._RTLIR_ifc_handlers:
            if isinstance( _obj, Type ):
              _obj_type = handler( _id, _obj )
              properties[ _id ] = _obj_type
              if isinstance( _obj_type, Array ):
                _add_packed_instances( _id, _obj_type, properties )
              break
      return Component( obj, properties )
    except AssertionError as e:
      msg = '' if e.args[0] is None else e.args[0]
      raise RTLIRConversionError( obj, msg )

  def _handle_Component( self, c_id, obj ):
    properties = {}
    collected_objs = collect_objs( obj, object )
    for _id, _obj in collected_objs:
      # Untranslatable attributes will be ignored
      if is_rtlir_convertible( _obj ):
        _obj_type = self.get_rtlir( _obj )
        if _obj_type is not None:
          properties[ _id ] = _obj_type
          if isinstance( _obj_type, Array ):
            _add_packed_instances( _id, _obj_type, properties )
      # TODO: Figure out a way to inform user of dropped attributes without
      # flooding STDOUT
      # else:
        # err_msg = \
  # """\
   # - Note: {} attribute {} of {} was dropped during conversion to RTLIR because it is
           # not a port, a, wire, an interface, a component, a constantor, or a
           # list of them. \
  # """
        # print( err_msg.format( _id, _obj, c_id ) )
    return Component( obj, properties )

  def _get_rtlir_uncached( self, _obj ):
    # global uncached
    """Return an RTLIR instance corresponding to `obj`."""
    obj = _freeze( _obj )

    try:
      for Type, handler in self._RTLIR_handlers:
        if isinstance( _obj, Type ):
          # uncached +=1
          # if uncached % 100 == 0:
            # print('uncached', uncached, repr(_obj), handler)
          return handler( "<NA>", _obj )
      if is_bitstruct_inst( _obj ):
        return self._handle_Const( "<NA>", _obj )

      # Cannot convert `obj` into RTLIR representation
      assert False, f'unrecognized object {_obj}!'
    except AssertionError as e:
      msg = '' if e.args[0] is None else e.args[0]
      raise RTLIRConversionError( _obj, msg )

  def _get_rtlir_cached( self, _obj ):
    """Return an RTLIR instance corresponding to `obj`."""
    obj = _freeze( _obj )
    if obj in self._rtlir_cache:
      # self.cache_hit += 1
      # if self.cache_hit % 100 == 0:
        # print("hit", self.cache_hit, repr(_obj))
      return self._rtlir_cache[ obj ]
    else:
      # self.cache_miss += 1
      # if self.cache_miss % 100 == 0:
        # print("miss", self.cache_miss, repr(_obj))
      try:
        for Type, handler in self._RTLIR_handlers:
          if isinstance( _obj, Type ):
            ret = self._rtlir_cache[ obj ] = handler( NA, _obj )
            return ret
        if is_bitstruct_inst( _obj ):
          ret = self._rtlir_cache[ obj ] = self._handle_Const( NA, _obj )
          return ret

        # Cannot convert `obj` into RTLIR representation
        assert False, f'unrecognized object {_obj}!'
      except AssertionError as e:
        msg = '' if e.args[0] is None else e.args[0]
        raise RTLIRConversionError( _obj, msg )

  def _handle_Array( self, _id, _obj ):
    if not _obj: return None

    obj = _obj
    ref_type = self.get_rtlir( obj[0] )
    for x in obj[1:]:
      assert self.get_rtlir(x) == ref_type, \
             f'all elements of array {obj} must have the same type {repr(ref_type)}!'

    dim_sizes = []
    while isinstance( obj, list ):
      if not obj:
        return None
      dim_sizes.append( len( obj ) )
      obj = obj[0]
    if isinstance( obj, ( int, Bits ) ):
      return Array( dim_sizes, self.get_rtlir( obj ), _obj )
    else:
      return Array( dim_sizes, self.get_rtlir( obj ) )

  def _handle_InPort( self, p_id, obj ):
    return Port( 'input', get_rtlir_dtype( obj ) )

  def _handle_OutPort( self, p_id, obj ):
    return Port( 'output', get_rtlir_dtype( obj ) )

  def _handle_Wire( self, w_id, obj ):
    return Wire( get_rtlir_dtype( obj ) )

  def _handle_Const( self, c_id, obj ):
    return Const( get_rtlir_dtype( obj ), obj )

  def _handle_Interface( self, i_id, obj ):
    properties = {}
    collected_objs = collect_objs( obj, object )
    for _id, _obj in collected_objs:
      if _is_rtlir_ifc_convertible( _obj ):
        _obj_type = self.get_rtlir( _obj )
        if _obj_type is not None:
          properties[ _id ] = _obj_type
          if isinstance( _obj_type, Array ):
            _add_packed_instances( _id, _obj_type, properties )
      # TODO: Figure out a way to inform user of dropped attributes without
      # flooding STDOUT
      # else:
        # err_msg = \
  # """\
   # - Note: {} attribute {} of {} was dropped during conversion to RTLIR because it is
           # not an interface, a port, or a list of them. \
  # """
        # print( err_msg.format( _id, _obj, i_id ) )
    return InterfaceView( obj.__class__.__name__, properties, obj )

  def _handle_Component( self, c_id, obj ):
    properties = {}
    collected_objs = collect_objs( obj, object )
    for _id, _obj in collected_objs:
      # Untranslatable attributes will be ignored
      if is_rtlir_convertible( _obj ):
        _obj_type = self.get_rtlir( _obj )
        if _obj_type is not None:
          properties[ _id ] = _obj_type
          if isinstance( _obj_type, Array ):
            _add_packed_instances( _id, _obj_type, properties )
      # TODO: Figure out a way to inform user of dropped attributes without
      # flooding STDOUT
      # else:
        # err_msg = \
  # """\
   # - Note: {} attribute {} of {} was dropped during conversion to RTLIR because it is
           # not a port, a, wire, an interface, a component, a constantor, or a
           # list of them. \
  # """
        # print( err_msg.format( _id, _obj, c_id ) )
    return Component( obj, properties )
