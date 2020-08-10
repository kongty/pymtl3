import inspect
from scipy.interpolate import interp1d
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
  bit = [0, 4, 8]
  energy = [0, 8.04e-14, 1.53e-13]
  f_energy = interp1d(bit, energy, fill_value='extrapolate', kind='linear')
  ret = f_energy(nbits).tolist()
  return ret

def get_sub_energy(nbits):
  bit = [0, 4, 8]
  energy = [0, 8.04e-14, 1.53e-13]
  f_energy = interp1d(bit, energy, fill_value='extrapolate', kind='linear')
  ret = f_energy(nbits).tolist()
  return ret

def get_mul_energy(nbits):
  bit = [0, 4, 8, 12]
  energy = [0, 2.26e-13, 8.23e-13, 1.24e-12]
  f_energy = interp1d(bit, energy, fill_value='extrapolate', kind='cubic')
  ret = f_energy(nbits).tolist()
  return ret

def get_pipeline_energy(nbits):
  bit = [0, 4, 8]
  energy = [0, 9.47e-14, 1.33e-13]
  f_energy = interp1d(bit, energy, fill_value='extrapolate', kind='linear')
  ret = f_energy(nbits).tolist()
  return ret

def get_register_energy(nbits):
  bit = [0, 4, 8]
  energy = [0, 9.47e-14, 1.33e-13]
  f_energy = interp1d(bit, energy, fill_value='extrapolate', kind='linear')
  ret = f_energy(nbits).tolist()
  return ret
