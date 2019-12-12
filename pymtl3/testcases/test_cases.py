"""
=========================================================================
test_cases.py
=========================================================================
Centralized test case repository.

Author : Peitian Pan
Date   : Dec 12, 2019
"""

from copy import copy, deepcopy

from pymtl3 import *
from pymtl3.passes.rtlir import RTLIRDataType as rdt

from .TestCase import AliasOf

#-------------------------------------------------------------------------
# Commonly used global variables
#-------------------------------------------------------------------------

pymtl_Bits_global_freevar = Bits32( 42 )

#-------------------------------------------------------------------------
# Commonly used BitStructs
#-------------------------------------------------------------------------

@bitstruct
class Bits32Foo:
  foo: Bits32

@bitstruct
class Bits32x5Foo:
  foo: [ Bits32 ] * 5

#-------------------------------------------------------------------------
# Commonly used Interfaces
#-------------------------------------------------------------------------

class Bits32OutIfc( Interface ):
  def construct( s ):
    s.foo = OutPort( Bits32 )

class Bits32InIfc( Interface ):
  def construct( s ):
    s.foo = InPort( Bits32 )

class Bits32InValRdyIfc( Interface ):
  def construct( s ):
    s.msg = InPort( Bits32 )
    s.val = InPort( Bits1 )
    s.rdy = OutPort( Bits1 )

class Bits32OutValRdyIfc( Interface ):
  def construct( s ):
    s.msg = OutPort( Bits32 )
    s.val = OutPort( Bits1 )
    s.rdy = InPort( Bits1 )

class Bits32MsgRdyIfc( Interface ):
  def construct( s ):
    s.msg = OutPort( Bits32 )
    s.rdy = InPort ( Bits1 )

class Bits32FooWireBarInIfc( Interface ):
  def construct( s ):
    s.foo = Wire( Bits32 )
    s.bar = InPort( Bits32 )

#-------------------------------------------------------------------------
# Commonly used Components
#-------------------------------------------------------------------------

class Bits32InOutComp( Component ):
  def construct( s ):
    s.in_ = InPort( Bits32 )
    s.out = OutPort( Bits32 )

class Bits16InOutPassThroughComp( Component ):
  def construct( s ):
    s.in_ = InPort( Bits16 )
    s.out = OutPort( Bits16 )
    @s.update
    def pass_through():
      s.out = s.in_

class Bits1OutComp( Component ):
  def construct( s ):
    s.out = OutPort( Bits1 )

class Bits32OutComp( Component ):
  def construct( s ):
    s.out = OutPort( Bits32 )

class Bits32OutDrivenComp( Component ):
  def construct( s ):
    s.out = OutPort( Bits32 )
    connect( s.out, Bits32(42) )

class WrappedBits32OutComp( Component ):
  def construct( s ):
    s.comp = Bits32OutComp()

#-------------------------------------------------------------------------
# Test Components
#-------------------------------------------------------------------------

class CaseBits32PortOnly:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32 )

class CaseStructPortOnly:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32Foo )

class CasePackedArrayStructPortOnly:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32x5Foo )

class CaseBits32x5PortOnly:
  class DUT( Component ):
    def construct( s ):
      s.in_ = [ InPort( Bits32 ) for _ in range(5) ]

class CaseBits32x5WireOnly:
  class DUT( Component ):
    def construct( s ):
      s.in_ = [ Wire( Bits32 ) for _ in range(5) ]

class CaseBits32x5ConstOnly:
  class DUT( Component ):
    def construct( s ):
      s.in_ = [ Bits32(42) for _ in range(5) ]

class CaseBits32MsgRdyIfcOnly:
  class DUT( Component ):
    def construct( s ):
      s.in_ = [ Bits32MsgRdyIfc() for _ in range(5) ]

class CaseBits32InOutx5CompOnly:
  class DUT( Component ):
    def construct( s ):
      s.b = [ Bits32InOutComp() for _ in range(5) ]

class CaseBits32Outx3x2x1PortOnly:
  class DUT( Component ):
    def construct( s ):
      s.out = [[[OutPort(Bits32) for _ in range(1)] for _ in range(2)] for _ in range(3)]

class CaseBits32WireIfcOnly:
  class DUT( Component ):
    def construct( s ):
      s.in_ = Bits32FooWireBarInIfc()

class CaseBits32ClosureConstruct:
  class DUT( Component ):
    def construct( s ):
      foo = Bits32( 42 )
      s.fvar_ref = foo
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = foo

class CaseBits32ClosureGlobal:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = pymtl_Bits_global_freevar

class CaseStructClosureGlobal:
  class DUT( Component ):
    def construct( s ):
      foo = InPort( Bits32Foo )
      s._foo = foo
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = foo.foo

class CaseReducesInx3OutComp:
  class DUT( Component ):
    def construct( s ):
      s.in_1 = InPort( Bits32 )
      s.in_2 = InPort( Bits32 )
      s.in_3 = InPort( Bits32 )
      s.out = OutPort( Bits1 )
      @s.update
      def v_reduce():
        s.out = reduce_and( s.in_1 ) & reduce_or( s.in_2 ) | reduce_xor( s.in_3 )

class CaseBits16IndexBasicComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = [ InPort( Bits16 ) for _ in range( 4 ) ]
      s.out = [ OutPort( Bits16 ) for _ in range( 2 ) ]
      @s.update
      def index_basic():
        s.out[ 0 ] = s.in_[ 0 ] + s.in_[ 1 ]
        s.out[ 1 ] = s.in_[ 2 ] + s.in_[ 3 ]

class CaseBits8Bits16MismatchAssignComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits16 )
      s.out = OutPort( Bits8 )
      @s.update
      def mismatch_width_assign():
        s.out = s.in_

class CaseBits32Bits64SlicingBasicComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32 )
      s.out = OutPort( Bits64 )
      @s.update
      def slicing_basic():
        s.out[ 0:16 ] = s.in_[ 16:32 ]
        s.out[ 16:32 ] = s.in_[ 0:16 ]

class CaseBits16ConstAddComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits16 )
      s.out = OutPort( Bits16 )
      @s.update
      def bits_basic():
        s.out = s.in_ + Bits16( 10 )

class CaseSlicingOverIndexComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = [ InPort( Bits16 ) for _ in range( 10 ) ]
      s.out = [ OutPort( Bits16 ) for _ in range( 5 ) ]
      @s.update
      def index_bits_slicing():
        s.out[0][0:8] = s.in_[1][8:16] + s.in_[2][0:8] + Bits8( 10 )
        s.out[1] = s.in_[3][0:16] + s.in_[4] + Bits16( 1 )

class CaseSubCompAddComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits16 )
      s.out = OutPort( Bits16 )
      s.b = Bits16InOutPassThroughComp()
      # There should be a way to check module connections?
      connect( s.in_, s.b.in_ )
      @s.update
      def multi_components_A():
        s.out = s.in_ + s.b.out

class CaseIfBasicComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits16 )
      s.out = OutPort( Bits8 )
      @s.update
      def if_basic():
        if s.in_[ 0:8 ] == Bits8( 255 ):
          s.out = s.in_[ 8:16 ]
        else:
          s.out = Bits8( 0 )

class CaseForBasicComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits16 )
      s.out = OutPort( Bits8 )
      @s.update
      def for_basic():
        for i in range( 8 ):
          s.out[ 2*i:2*i+1 ] = s.in_[ 2*i:2*i+1 ] + s.in_[ 2*i+1:(2*i+1)+1 ]

class CaseTwoUpblksSliceComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits4 )
      s.out = OutPort( Bits8 )
      @s.update
      def multi_upblks_1():
        s.out[ 0:4 ] = s.in_
      @s.update
      def multi_upblks_2():
        s.out[ 4:8 ] = s.in_

class CaseFlipFlopAdder:
  class DUT( Component ):
    def construct( s ):
      s.in0 = InPort( Bits32 )
      s.in1 = InPort( Bits32 )
      s.out0 = OutPort( Bits32 )
      @s.update_ff
      def update_ff_upblk():
        s.out0 <<= s.in0 + s.in1

class CaseConstSizeSlicingComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits16 )
      s.out = [ OutPort( Bits8 ) for _ in range(2) ]
      @s.update
      def upblk():
        for i in range(2):
          s.out[i] = s.in_[i*8 : i*8 + 8]

class CaseBits32TmpWireComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32 )
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        u = s.in_ + Bits32(42)
        s.out = u

class CaseStructTmpWireComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32Foo )
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        u = s.in_
        s.out = u.foo

class CaseTmpWireOverwriteConflictComp:
  class DUT( Component ):
    def construct( s ):
      s.in_1 = InPort( Bits32 )
      s.in_2 = InPort( Bits16 )
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        u = s.in_1 + Bits32(42)
        u = s.in_2 + Bits16(1)
        s.out = u

class CaseScopeTmpWireOverwriteConflictComp:
  class DUT( Component ):
    def construct( s ):
      s.in_1 = InPort( Bits32 )
      s.in_2 = InPort( Bits16 )
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        if 1:
          u = s.in_1 + Bits32(42)
          s.out = u
        else:
          u = s.in_2 + Bits16(1)
          s.out = u

#-------------------------------------------------------------------------
# Test cases without errors
#-------------------------------------------------------------------------

class CaseLambdaConnectComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32 )
      s.out = OutPort( Bits32 )
      s.out //= lambda: s.in_ + Bits32(42)

class CaseBits32FooInBits32OutComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32Foo )
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = s.in_.foo

class CaseBits32FooKwargComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = Bits32Foo( foo = Bits32( 42 ) )

class CaseBits32FooInstantiationComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32Foo )
      @s.update
      def upblk():
        s.out = Bits32Foo( Bits32( 42 ) )

class CaseConstStructInstComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = Bits32Foo()
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = s.in_.foo

class CaseInterfaceAttributeComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = Bits32OutIfc()
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = s.in_.foo

class CaseArrayInterfacesComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = [ Bits32OutIfc() for _ in range(4) ]
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = s.in_[2].foo

class CaseBits32SubCompPassThroughComp:
  class DUT( Component ):
    def construct( s ):
      s.comp = Bits32OutComp()
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = s.comp.out

class CaseArrayBits32SubCompPassThroughComp:
  class DUT( Component ):
    def construct( s ):
      s.comp = [ Bits32OutComp() for _ in range(4) ]
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = s.comp[2].out

class CaseConstBits32AttrComp:
  class DUT( Component ):
    def construct( s ):
      s.const = [ Bits32(42) for _ in range(5) ]

class CaseInx2Outx2ConnectComp:
  class DUT( Component ):
    def construct( s ):
      s.in_1 = InPort( Bits32 )
      s.in_2 = InPort( Bits32 )
      s.out1 = OutPort( Bits32 )
      s.out2 = OutPort( Bits32 )
      connect( s.in_1, s.out1 )
      connect( s.in_2, s.out2 )

class CaseConnectPortIndexComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = [ InPort( Bits32 ) for _ in range(5) ]
      s.out = OutPort( Bits32 )
      connect( s.in_[2], s.out )

class CaseConnectInToWireComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = [ InPort( Bits32 ) for _ in range(5) ]
      s.wire = [ Wire( Bits32 ) for _ in range(5) ]
      s.out = OutPort( Bits32 )
      connect( s.wire[2], s.out )
      for i in range(5):
        connect( s.wire[i], s.in_[i] )

class CaseConnectConstToOutComp:
  class DUT( Component ):
    def construct( s ):
      s.const = [ 42 for _ in range(5) ]
      s.out = OutPort( Bits32 )
      connect( s.const[2], s.out )

class CaseConnectBitSelToOutComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32 )
      s.out = OutPort( Bits1 )
      connect( s.in_[0], s.out )

class CaseConnectSliceToOutComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32 )
      s.out = OutPort( Bits4 )
      connect( s.in_[4:8], s.out )

class CaseConnectBitsConstToOutComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      connect( s.out, Bits32(0) )

class CaseConnectStructAttrToOutComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32Foo )
      s.out = OutPort( Bits32 )
      connect( s.out, s.in_.foo )

class CaseConnectArrayStructAttrToOutComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32x5Foo )
      s.out = OutPort( Bits32 )
      connect( s.out, s.in_.foo[1] )

class CaseBits32IfcInComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = Bits32InIfc()
      s.out = OutPort( Bits32 )
      connect( s.out, s.in_.foo )

class CaseArrayBits32IfcInComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = [ Bits32InIfc() for _ in range(5) ]
      s.out = OutPort( Bits32 )
      connect( s.in_[2].foo, s.out )

class CaseConnectValRdyIfcComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = Bits32InValRdyIfc()
      s.out = Bits32OutValRdyIfc()
      # This will be automatically extended to connect all signals in
      # this interface!
      connect( s.out, s.in_ )

class CaseBits32ConnectSubCompAttrComp:
  class DUT( Component ):
    def construct( s ):
      s.b = Bits32OutDrivenComp()
      s.out = OutPort( Bits32 )
      connect( s.out, s.b.out )

class CaseBits32ArrayConnectSubCompAttrComp:
  class DUT( Component ):
    def construct( s ):
      s.b = [ Bits32OutDrivenComp() for _ in range(5) ]
      s.out = OutPort( Bits32 )
      connect( s.out, s.b[1].out )

#-------------------------------------------------------------------------
# Test cases that contain errors
#-------------------------------------------------------------------------

class CaseStructBitsUnagreeableComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32Foo )
      s.out = OutPort( Bits16 )
      @s.update
      def upblk():
        s.out = s.in_

class CaseConcatComponentComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits8 )
      s.out = OutPort( Bits16 )
      @s.update
      def upblk():
        s.out = concat( s, s.in_ )

class CaseZextVaribleNbitsComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits8 )
      s.out = OutPort( Bits16 )
      @s.update
      def upblk():
        s.out = zext( s.in_, s.in_ )

class CaseZextSmallNbitsComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits8 )
      s.out = OutPort( Bits16 )
      @s.update
      def upblk():
        s.out = zext( s.in_, 4 )

class CaseSextVaribleNbitsComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits8 )
      s.out = OutPort( Bits16 )
      @s.update
      def upblk():
        s.out = sext( s.in_, s.in_ )

class CaseSextSmallNbitsComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits8 )
      s.out = OutPort( Bits16 )
      @s.update
      def upblk():
        s.out = sext( s.in_, 4 )

class CaseDroppedAttributeComp:
  class DUT( Component ):
    def construct( s ):
      # s.in_ is not recognized by RTLIR and will be dropped
      s.in_ = 'string'
      s.out = OutPort( Bits16 )
      @s.update
      def upblk():
        s.out = s.in_

class CaseL1UnsupportedSubCompAttrComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits4 )
      s.out = [ OutPort( Bits1 ) for _ in range(5) ]
      s.comp_array = [ Bits1OutComp() for _ in range(5) ]
      @s.update
      def upblk():
        s.out = s.comp_array[ 0 ].out

class CaseIndexOutOfRangeComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = [ InPort( Bits1 ) for _ in range(4) ]
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = s.in_[4]

class CaseBitSelOutOfRangeComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits4 )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = s.in_[4]

class CaseIndexOnStructComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32x5Foo )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = s.in_[16]

class CaseSliceOnStructComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32x5Foo )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = s.in_[0:16]

class CaseSliceBoundLowerComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits4 )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = s.in_[4:0]

class CaseSliceVariableBoundComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits4 )
      s.slice_l = InPort( Bits2 )
      s.slice_r = InPort( Bits2 )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = s.in_[s.slice_l:s.slice_r]

class CaseSliceOutOfRangeComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits4 )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = s.in_[0:5]

class CaseLHSConstComp:
  class DUT( Component ):
    def construct( s ):
      u, s.v = 42, 42
      @s.update
      def upblk():
        s.v = u

class CaseLHSComponentComp:
  class DUT( Component ):
    def construct( s ):
      s.u = Bits16InOutPassThroughComp()
      @s.update
      def upblk():
        s.u = 42

class CaseRHSComponentComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = s

class CaseZextOnComponentComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = zext( s, 1 )

class CaseSextOnComponentComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = sext( s, 1 )

class CaseSizeCastComponentComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = Bits32( s )

class CaseAttributeSignalComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32Foo )
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = s.in_.foo

class CaseComponentInIndexComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32 )
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = s.in_[ s ]

class CaseComponentBaseIndexComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = s[ 1 ]

class CaseComponentLowerSliceComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32 )
      s.idx = Bits16InOutPassThroughComp()
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        s.out = s.in_[ s.idx:4 ]

class CaseComponentHigherSliceComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32 )
      s.idx = Bits16InOutPassThroughComp()
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        s.out = s.in_[ 0:s.idx ]

class CaseSliceOnComponentComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = s[ 0:4 ]

class CaseUpblkArgComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk( number ):
        u = number

class CaseAssignMultiTargetComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        u = v = x = y

class CaseCopyArgsComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        u = copy(42, 10)

class CaseDeepcopyArgsComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        u = deepcopy(42, 10)

class CaseSliceWithStepsComp:
  class DUT( Component ):
    def construct( s ):
      v = 42
      @s.update
      def upblk():
        u = v[ 0:16:4 ]

class CaseExtendedSubscriptComp:
  class DUT( Component ):
    def construct( s ):
      v = 42
      @s.update
      def upblk():
        u = v[ 0:8, 16:24 ]

class CaseTmpComponentComp:
  class DUT( Component ):
    def construct( s ):
      v = Bits16InOutPassThroughComp()
      @s.update
      def upblk():
        u = v

class CaseUntypedTmpComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        u = 42

class CaseStarArgsComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        x = x(*x)

class CaseDoubleStarArgsComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        x = x(**x)

class CaseKwArgsComp:
  class DUT( Component ):
    def construct( s ):
      xx = 42
      @s.update
      def upblk():
        x = x(x=x)

class CaseNonNameCalledComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        x = copy.copy( x )

class CaseFuncNotFoundComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        t = undefined_func(u)

class CaseBitsArgsComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        x = Bits32( 42, 42 )

class CaseConcatNoArgsComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        x = concat()

class CaseZextTwoArgsComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        x = zext( s )

class CaseSextTwoArgsComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        x = sext( s )

class CaseUnrecognizedFuncComp:
  class DUT( Component ):
    def construct( s ):
      def foo(): pass
      @s.update
      def upblk():
        x = foo()

class CaseStandaloneExprComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        42

class CaseLambdaFuncComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = lambda: 42

class CaseDictComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = { 1:42 }

class CaseSetComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = { 42 }

class CaseListComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = [ 42 ]

class CaseTupleComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = ( 42, )

class CaseListComprehensionComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = [ 42 for _ in range(1) ]

class CaseSetComprehensionComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = { 42 for _ in range(1) }

class CaseDictComprehensionComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = { 1:42 for _ in range(1) }

class CaseGeneratorExprComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = ( 42 for _ in range(1) )

class CaseYieldComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = yield

class CaseReprComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        # Python 2 only: s.out = `42`
        s.out = repr(42)

class CaseStrComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = '42'

class CaseClassdefComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        class c: pass

class CaseDeleteComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        del u

class CaseWithComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        with u: 42

class CaseRaiseComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        raise 42

class CaseTryExceptComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        try: 42
        except: 42

class CaseTryFinallyComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        try: 42
        finally: 42

class CaseImportComp:
  class DUT( Component ):
    def construct( s ):
      x = 42
      @s.update
      def upblk():
        import x

class CaseImportFromComp:
  class DUT( Component ):
    def construct( s ):
      x = 42
      @s.update
      def upblk():
        from x import x

class CaseExecComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        # Python 2 only: exec 42
        exec(42)

class CaseGlobalComp:
  class DUT( Component ):
    def construct( s ):
      u = 42
      @s.update
      def upblk():
        global u

class CasePassComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        pass

class CaseWhileComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        while 42: 42

class CaseExtSliceComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        42[ 1:2:3, 2:4:6 ]

class CaseAddComponentComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = Bits1( 1 ) + s

class CaseInvComponentComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = ~s

class CaseComponentStartRangeComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        for i in range( s, 8, 1 ):
          s.out = ~Bits1( 1 )

class CaseComponentEndRangeComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        for i in range( 0, s, 1 ):
          s.out = ~Bits1( 1 )

class CaseComponentStepRangeComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        for i in range( 0, 8, s ):
          s.out = ~Bits1( 1 )

class CaseComponentIfCondComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        if s:
          s.out = Bits1( 1 )
        else:
          s.out = ~Bits1( 1 )

class CaseComponentIfExpCondComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = Bits1(1) if s else ~Bits1(1)

class CaseComponentIfExpBodyComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = s if 1 else ~Bits1(1)

class CaseComponentIfExpElseComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = Bits1(1) if 1 else s

class CaseStructIfCondComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32Foo )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        if s.in_:
          s.out = Bits1(1)
        else:
          s.out = ~Bits1(1)

class CaseZeroStepRangeComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        for i in range( 0, 4, 0 ):
          s.out = Bits1( 1 )

class CaseVariableStepRangeComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits2 )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        for i in range( 0, 4, s.in_ ):
          s.out = Bits1( 1 )

class CaseStructIfExpCondComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32Foo )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = Bits1(1) if s.in_ else ~Bits1(1)

class CaseDifferentTypesIfExpComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32Foo )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = Bits1(1) if 1 else s.in_

class CaseNotStructComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32Foo )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = not s.in_

class CaseAndStructComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32Foo )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = Bits1( 1 ) and s.in_

class CaseAddStructBits1Comp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32Foo )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = Bits1( 1 ) + s.in_

class CaseExplicitBoolComp:
  class DUT( Component ):
    def construct( s ):
      Bool = rdt.Bool
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = Bool( Bits1(1) )

class CaseTmpVarUsedBeforeAssignmentComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        s.out = u + Bits4( 1 )

class CaseForLoopElseComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        for i in range(4):
          s.out = Bits4( 1 )
        else:
          s.out = Bits4( 1 )

class CaseSignalAsLoopIndexComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = Wire( Bits4 )
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        for s.in_ in range(4):
          s.out = Bits4( 1 )

class CaseRedefLoopIndexComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        for i in range(4):
          for i in range(4):
            s.out = Bits4( 1 )

class CaseSignalAfterInComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits2 )
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        for i in s.in_:
          s.out = Bits4( 1 )

class CaseFuncCallAfterInComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits4 )
      def foo(): pass
      @s.update
      def upblk():
        for i in foo():
          s.out = Bits4( 1 )

class CaseNoArgsToRangeComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        for i in range():
          s.out = Bits4( 1 )

class CaseTooManyArgsToRangeComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        for i in range( 0, 4, 1, 1 ):
          s.out = Bits4( 1 )

class CaseInvalidIsComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        s.out = Bits1( 1 ) is Bits1( 1 )

class CaseInvalidIsNotComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        s.out = Bits1( 1 ) is not Bits1( 1 )

class CaseInvalidInComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        s.out = Bits1( 1 ) in Bits1( 1 )

class CaseInvalidNotInComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        s.out = Bits1( 1 ) not in Bits1( 1 )

class CaseInvalidDivComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        s.out = Bits1( 1 ) // Bits1( 1 )

class CaseMultiOpComparisonComp:
  class DUT( Component ):
    def construct( s ):
      s.out = OutPort( Bits4 )
      @s.update
      def upblk():
        s.out = Bits1( 0 ) <= Bits2( 1 ) <= Bits2( 2 )

class CaseInvalidBreakComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        for i in range(42): break

class CaseInvalidContinueComp:
  class DUT( Component ):
    def construct( s ):
      @s.update
      def upblk():
        for i in range(42): continue

class CaseBitsAttributeComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32 )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = s.in_.foo

class CaseStructMissingAttributeComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = InPort( Bits32Foo )
      s.out = OutPort( Bits1 )
      @s.update
      def upblk():
        s.out = s.in_.bar

class CaseInterfaceMissingAttributeComp:
  class DUT( Component ):
    def construct( s ):
      s.in_ = Bits32OutIfc()
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = s.in_.bar

class CaseSubCompMissingAttributeComp:
  class DUT( Component ):
    def construct( s ):
      s.comp = Bits32OutComp()
      s.out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.out = s.comp.bar

class CaseCrossHierarchyAccessComp:
  class DUT( Component ):
    def construct( s ):
      s.comp = WrappedBits32OutComp()
      s.a_out = OutPort( Bits32 )
      @s.update
      def upblk():
        s.a_out = s.comp.comp.out
