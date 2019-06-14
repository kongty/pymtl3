#=========================================================================
# SVStructuralTranslatorL2_test.py
#=========================================================================
# Author : Peitian Pan
# Date   : May 29, 2019
"""Test the level 2 SystemVerilog structural translator."""

from __future__ import absolute_import, division, print_function

from pymtl3.datatypes import Bits1, Bits32, BitStruct
from pymtl3.dsl import Component, InPort, OutPort, Wire
from pymtl3.passes.rtlir import RTLIRDataType as rdt
from pymtl3.passes.rtlir.util.test_utility import do_test
from pymtl3.passes.sverilog.translation.structural.SVStructuralTranslatorL2 import (
    SVStructuralTranslatorL2,
)

from .SVStructuralTranslatorL1_test import is_sverilog_reserved


def local_do_test( m ):
  m.elaborate()
  SVStructuralTranslatorL2.is_sverilog_reserved = is_sverilog_reserved
  tr = SVStructuralTranslatorL2( m )
  tr.clear( m )
  tr.translate_structural( m )

  ports = tr.structural.decl_ports[m]
  assert ports == m._ref_ports[m]
  wires = tr.structural.decl_wires[m]
  assert wires == m._ref_wires[m]
  structs = tr.structural.decl_type_struct
  assert map(lambda x: x[0], structs) == map(lambda x: x[0], m._ref_structs)
  assert map(lambda x: x[1]['def'], structs) == map(lambda x: x[1], m._ref_structs)
  conns = tr.structural.connections[m]
  assert conns == m._ref_conns[m]

def test_struct_port( do_test ):
  class B( BitStruct ):
    def __init__( s, foo=42 ):
      s.foo = Bits32(foo)
  class A( Component ):
    def construct( s ):
      s.in_ = InPort( B )
      s.out = OutPort( Bits32 )
      s.connect( s.out, s.in_.foo )
  a = A()
  a._ref_structs = [
    ( rdt.Struct( 'B', {'foo':rdt.Vector(32)}, ['foo'] ), \
"""\
typedef struct packed {
  logic [31:0] foo;
} B;
""" ) ]
  a._ref_ports = { a : \
"""\
  input logic [0:0] clk,
  input B in_,
  output logic [31:0] out,
  input logic [0:0] reset\
""" }
  a._ref_wires = { a : "" }
  a._ref_conns = { a : \
"""\
  assign out = in_.foo;\
""" }

  # Yosys backend test reference output
  a._ref_ports_port_yosys = { a : \
"""\
  input logic [0:0] clk,
  input logic [31:0] in_$foo,
  output logic [31:0] out,
  input logic [0:0] reset\
""" }
  a._ref_ports_wire_yosys = { a : "" }
  a._ref_ports_conn_yosys = { a : "" }
  a._ref_wires_yosys = a._ref_wires
  a._ref_conns_yosys = { a : \
"""\
  assign out = in_$foo;\
""" }

  # TestVectorSimulator properties
  def tv_in( m, tv ):
    m.in_ = tv[0]
  def tv_out( m, tv ):
    assert m.out == Bits32(tv[1])
  a._test_vectors = [
    [       B(),   42 ],
    [    B( 0 ),    0 ],
    [   B( -1 ),   -1 ],
    [   B( -2 ),   -2 ],
    [   B( 24 ),   24 ],
  ]
  a._tv_in, a._tv_out = tv_in, tv_out
  do_test( a )

def test_nested_struct_port( do_test ):
  class C( BitStruct ):
    def __init__( s, bar=1 ):
      s.bar = Bits32(bar)
  class B( BitStruct ):
    def __init__( s, foo=42 ):
      s.foo = Bits32(foo)
      s.c = C()
  class A( Component ):
    def construct( s ):
      s.in_ = InPort( B )
      s.out_foo = OutPort( Bits32 )
      s.out_bar = OutPort( Bits32 )
      s.connect( s.out_foo, s.in_.foo )
      s.connect( s.out_bar, s.in_.c.bar )
  a = A()
  _C = rdt.Struct( 'C', {'bar':rdt.Vector(32)}, ['bar'] )
  a._ref_structs = [ ( _C, \
"""\
typedef struct packed {
  logic [31:0] bar;
} C;
""" ),
    ( rdt.Struct( 'B', {'c':_C, 'foo':rdt.Vector(32)}, ['c', 'foo'] ), \
"""\
typedef struct packed {
  C c;
  logic [31:0] foo;
} B;
""" ) ]
  a._ref_ports = { a : \
"""\
  input logic [0:0] clk,
  input B in_,
  output logic [31:0] out_bar,
  output logic [31:0] out_foo,
  input logic [0:0] reset\
""" }
  a._ref_wires = { a : "" }
  a._ref_conns = { a : \
"""\
  assign out_foo = in_.foo;
  assign out_bar = in_.c.bar;\
""" }

  # Yosys backend test reference output
  a._ref_ports_port_yosys = { a : \
"""\
  input logic [0:0] clk,
  input logic [31:0] in_$c$bar,
  input logic [31:0] in_$foo,
  output logic [31:0] out_bar,
  output logic [31:0] out_foo,
  input logic [0:0] reset\
""" }
  a._ref_ports_wire_yosys = { a : "" }
  a._ref_ports_conn_yosys = { a : "" }
  a._ref_wires_yosys = a._ref_wires
  a._ref_conns_yosys = { a : \
"""\
  assign out_foo = in_$foo;
  assign out_bar = in_$c$bar;\
""" }

  # TestVectorSimulator properties
  def tv_in( m, tv ):
    m.in_ = tv[0]
  def tv_out( m, tv ):
    assert m.out_foo == Bits32(tv[1])
    assert m.out_bar == Bits32(tv[2])
  a._test_vectors = [
    [       B(),    42,    1 ],
    [    B( 1 ),     1,    1 ],
    [   B( -1 ),    -1,    1 ],
    [   B( -2 ),    -2,    1 ],
    [   B( 24 ),    24,    1 ],
  ]
  a._tv_in, a._tv_out = tv_in, tv_out
  do_test( a )

def test_packed_array( do_test ):
  class B( BitStruct ):
    def __init__( s, foo=42 ):
      s.foo = [ Bits32(foo) for _ in range(2) ]
  class A( Component ):
    def construct( s ):
      s.in_ = InPort( B )
      s.out =  [ OutPort( Bits32 ) for _ in range(2) ]
      s.connect( s.out[0], s.in_.foo[0] )
      s.connect( s.out[1], s.in_.foo[1] )
  a = A()
  _foo = rdt.PackedArray( [2], rdt.Vector(32) )
  a._ref_structs = [
    ( rdt.Struct( 'B', {'foo':_foo}, ['foo'] ), \
"""\
typedef struct packed {
  logic [1:0][31:0] foo;
} B;
""" ) ]
  a._ref_ports = { a : \
"""\
  input logic [0:0] clk,
  input B in_,
  output logic [31:0] out [0:1],
  input logic [0:0] reset\
""" }
  a._ref_wires = { a : "" }
  a._ref_conns = { a : \
"""\
  assign out[0] = in_.foo[0];
  assign out[1] = in_.foo[1];\
""" }

  # Yosys backend test reference output
  a._ref_ports_port_yosys = { a : \
"""\
  input logic [0:0] clk,
  input logic [31:0] in_$foo$__0,
  input logic [31:0] in_$foo$__1,
  output logic [31:0] out$__0,
  output logic [31:0] out$__1,
  input logic [0:0] reset\
""" }
  a._ref_ports_wire_yosys = { a : \
"""\
  logic [31:0] in_$foo [0:1];
  logic [31:0] out [0:1];\
""" }
  a._ref_ports_conn_yosys = { a : \
"""\
  assign in_$foo[0] = in_$foo$__0;
  assign in_$foo[1] = in_$foo$__1;
  assign out$__0 = out[0];
  assign out$__1 = out[1];\
""" }
  a._ref_wires_yosys = a._ref_wires
  a._ref_conns_yosys = { a : \
"""\
  assign out[0] = in_$foo[0];
  assign out[1] = in_$foo[1];\
""" }

  # TestVectorSimulator properties
  def tv_in( m, tv ):
    m.in_ = tv[0]
  def tv_out( m, tv ):
    assert m.out[0] == Bits32(tv[1])
    assert m.out[1] == Bits32(tv[2])
  a._test_vectors = [
    [       B(),    42,   42 ],
    [    B( 1 ),     1,    1 ],
    [   B( -1 ),    -1,   -1 ],
    [   B( -2 ),    -2,   -2 ],
    [   B( 24 ),    24,   24 ],
  ]
  a._tv_in, a._tv_out = tv_in, tv_out
  do_test( a )

def test_struct_packed_array( do_test ):
  class C( BitStruct ):
    def __init__( s, bar=1 ):
      s.bar = Bits32(bar)
  class B( BitStruct ):
    def __init__( s ):
      s.c = [ C() for _ in range(2) ]
  class A( Component ):
    def construct( s ):
      s.in_ = InPort( B )
      s.out =  [ OutPort( Bits32 ) for _ in range(2) ]
      s.connect( s.out[0], s.in_.c[0].bar )
      s.connect( s.out[1], s.in_.c[1].bar )
  a = A()
  _C = rdt.Struct('C', {'bar':rdt.Vector(32)}, ['bar'])
  a._ref_structs = [
    ( _C, \
"""\
typedef struct packed {
  logic [31:0] bar;
} C;
""" ),
    ( rdt.Struct( 'B', {'c':rdt.PackedArray([2], _C)}, ['c'] ), \
"""\
typedef struct packed {
  C [1:0] c;
} B;
""" ) ]
  a._ref_ports = { a : \
"""\
  input logic [0:0] clk,
  input B in_,
  output logic [31:0] out [0:1],
  input logic [0:0] reset\
""" }
  a._ref_wires = { a : "" }
  a._ref_conns = { a : \
"""\
  assign out[0] = in_.c[0].bar;
  assign out[1] = in_.c[1].bar;\
""" }

  # Yosys backend test reference output
  a._ref_ports_port_yosys = { a : \
"""\
  input logic [0:0] clk,
  input logic [31:0] in_$c$__0$bar,
  input logic [31:0] in_$c$__1$bar,
  output logic [31:0] out$__0,
  output logic [31:0] out$__1,
  input logic [0:0] reset\
""" }
  a._ref_ports_wire_yosys = { a : \
"""\
  logic [31:0] in_$c$bar [0:1];
  logic [31:0] out [0:1];\
""" }
  a._ref_ports_conn_yosys = { a : \
"""\
  assign in_$c$bar[0] = in_$c$__0$bar;
  assign in_$c$bar[1] = in_$c$__1$bar;
  assign out$__0 = out[0];
  assign out$__1 = out[1];\
""" }
  a._ref_wires_yosys = a._ref_wires
  a._ref_conns_yosys = { a : \
"""\
  assign out[0] = in_$c$bar[0];
  assign out[1] = in_$c$bar[1];\
""" }

  # TestVectorSimulator properties
  def tv_in( m, tv ):
    m.in_ = tv[0]
  def tv_out( m, tv ):
    assert m.out[0] == Bits32(tv[1])
    assert m.out[1] == Bits32(tv[2])
  a._test_vectors = [
    [       B(),     1,    1 ],
  ]
  a._tv_in, a._tv_out = tv_in, tv_out
  do_test( a )
