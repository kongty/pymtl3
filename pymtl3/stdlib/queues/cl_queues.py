"""
========================================================================
queues.py
========================================================================
This file contains cycle-level queues.

Author : Shunning Jiang, Yanghui Ou
Date   : Mar 10, 2018
"""

from collections import deque

from pymtl3 import *
import inspect
import numpy as np
from ...energy.energy_plugin import *

#-------------------------------------------------------------------------
# PipeQueueCL
#-------------------------------------------------------------------------
def _get_bits(msg):
  # return total number of bits in message
  # Bits, bitstruct, array of Bits, 2d array of Bits, Class with bitstruct
  if hasattr(msg, 'nbits'):
    return msg.nbits
  elif type(msg) is list:
    nbits = 0
    msg_flattend = np.ndarray.flatten(np.array(msg))
    for i in msg_flattend:
      nbits += i.nbits
    return nbits
  elif type(msg) is np.ndarray:
    nbits = 0
    msg_flattend = np.ndarray.flatten(msg)
    for i in msg_flattend:
      nbits += i.nbits
    return nbits
  else:
    return 0

class PipeQueueCL( Component ):

  def construct( s, num_entries=1 ):
    s.queue = deque( maxlen=num_entries )

    s.add_constraints(
      M( s.peek   ) < M( s.enq  ),
      M( s.deq    ) < M( s.enq  )
    )

  @non_blocking( lambda s: len( s.queue ) < s.queue.maxlen )
  def enq( s, msg ):
    update_energy("pipeline", _get_bits(msg))
    s.queue.appendleft( msg )

  @non_blocking( lambda s: len( s.queue ) > 0 )
  def deq( s ):
    return s.queue.pop()

  @non_blocking( lambda s: len( s.queue ) > 0 )
  def peek( s ):
    return s.queue[-1]

  def line_trace( s ):
    return "{}( ){}".format( s.enq, s.deq )

#-------------------------------------------------------------------------
# BypassQueueCL
#-------------------------------------------------------------------------

class BypassQueueCL( Component ):

  def construct( s, num_entries=1 ):
    s.queue = deque( maxlen=num_entries )

    s.add_constraints(
      M( s.enq    ) < M( s.peek    ),
      M( s.enq    ) < M( s.deq     ),
    )

  @non_blocking( lambda s: len( s.queue ) < s.queue.maxlen )
  def enq( s, msg ):
    s.queue.appendleft( msg )

  @non_blocking( lambda s: len( s.queue ) > 0 )
  def deq( s ):
    return s.queue.pop()

  @non_blocking( lambda s: len( s.queue ) > 0 )
  def peek( s ):
    return s.queue[-1]

  def line_trace( s ):
    return "{}( ){}".format( s.enq, s.deq )

#-------------------------------------------------------------------------
# NormalQueueCL
#-------------------------------------------------------------------------

class NormalQueueCL( Component ):

  def construct( s, num_entries=1 ):
    s.queue = deque( maxlen=num_entries )
    s.enq_rdy = False
    s.deq_rdy = False

    @update
    def up_pulse():
      s.enq_rdy = len( s.queue ) < s.queue.maxlen
      s.deq_rdy = len( s.queue ) > 0

    s.add_constraints(
      U( up_pulse ) < M( s.enq.rdy ),
      U( up_pulse ) < M( s.deq.rdy ),
      M( s.peek   ) < M( s.deq.rdy  ),
      M( s.peek   ) < M( s.enq.rdy  )
    )

  @non_blocking( lambda s: s.enq_rdy )
  def enq( s, msg ):
    s.queue.appendleft( msg )

  @non_blocking( lambda s: s.deq_rdy )
  def deq( s ):
    return s.queue.pop()

  @non_blocking( lambda s: len( s.queue ) > 0 )
  def peek( s ):
    return s.queue[-1]

  def line_trace( s ):
    return "{}( ){}".format( s.enq, s.deq )
