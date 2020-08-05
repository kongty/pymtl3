import inspect
from collections import defaultdict

# helper functions
def _get_func_name():
  _frame = inspect.currentframe().f_back.f_back
  _name = inspect.getframeinfo(_frame).function
  return _name

def _get_caller():
  _frame = inspect.currentframe()
  while 's' not in _frame.f_locals or not hasattr(_frame.f_locals['s'], 'energy'):
    _frame = _frame.f_back
    if _frame is None or _frame.f_locals is None:
      return None

  # caller object
  return _frame.f_locals["s"]

# update compute energy
def update_energy(name, nbits):
  group, _energy = get_group_energy(name, nbits)
  caller = _get_caller()

  if caller is None:
    return
  elif type(_get_caller().energy[group][name]) == defaultdict:
    _get_caller().energy[group][name] = _energy
  else:
    _get_caller().energy[group][name] += _energy

# energy table
def get_group_energy(name, nbits):
  if name == "add":
    ret = get_add_energy(nbits)
    group = 'comp'
  elif name == "sub":
    ret = get_sub_energy(nbits)
    group = 'comp'
  elif name == "mul":
    ret = get_mul_energy(nbits)
    group = 'comp'
  elif name == "pipeline":
    ret = get_pipeline_energy(nbits)
    group = 'seq'
  elif name == "register":
    ret = get_register_energy(nbits)
    group = 'seq'
  else:
    ret = 1
    group = 'misc'
  return group, ret

##################################################
# dummy energy
##################################################
def get_add_energy(nbits):
  ret = 1 * nbits
  return ret

def get_sub_energy(nbits):
  ret = 2 * nbits
  return ret

def get_mul_energy(nbits):
  ret = 4 * nbits
  return ret

def get_pipeline_energy(nbits):
  ret = 8 * nbits
  return ret

def get_register_energy(nbits):
  ret = 7 * nbits
  return ret
