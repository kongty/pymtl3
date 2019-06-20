"""
=========================================================================
 ProcRTL_test.py
=========================================================================

Author : Shunning Jiang, Yanghui Ou
  Date : June 15, 2019
"""
import pytest
import random
random.seed(0xdeadbeef)

from pymtl3  import *
from examples.ex03_proc.ProcRTL import ProcRTL

#-------------------------------------------------------------------------
# ProcRTL_Tests
#-------------------------------------------------------------------------
# It is as simple as inheriting from CL tests and change the ProcType to
# use.

from .ProcCL_test import ProcCL_Tests as BaseTests

class ProcRTL_Tests( BaseTests ):

  @classmethod
  def setup_class( cls ):
    cls.ProcType = ProcRTL