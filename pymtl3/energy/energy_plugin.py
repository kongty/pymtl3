import inspect
from scipy.interpolate import interp1d
from collections import defaultdict
import math

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
def update_energy(name, n_elem, mem_byte_width=0):
  _energy = get_energy(name, n_elem, mem_byte_width)
  caller = _get_caller()

  if caller is None:
    return
  else:
    _get_caller().energy[name] += _energy

# energy table
def get_energy(name, n_elem, mem_byte_width):
  if name == "add":
    ret = get_add_energy(n_elem)
  elif name == "sub":
    ret = get_sub_energy(n_elem)
  elif name == "mul":
    ret = get_mul_energy(n_elem)
  elif name == "pipeline":
    ret = get_pipeline_energy(n_elem)
  elif name == "register":
    ret = get_register_energy(n_elem)
  elif name == "read":
    ret = get_mem_read_energy(n_elem, mem_byte_width)
  elif name == "write":
    ret = get_mem_write_energy(n_elem, mem_byte_width)
  else:
    ret = 1
  return ret

##################################################
# dummy energy
##################################################
def get_add_energy(n_elem):
  bit = [0, 8, 12, 24]
  # energy = [0, 1.38e-13, 2.06e-13, 3.04e-13]
  energy = [0, 1.38e-13, 2.06e-13, 3.04e-13]
  energy = [ele * 0.5 for ele in energy]
  f_energy = interp1d(bit, energy, fill_value='extrapolate', kind='linear')
  ret = f_energy(n_elem).tolist()
  return ret

def get_sub_energy(n_elem):
  ret = get_add_energy(n_elem)
  return ret

def get_mul_energy(n_elem):
  bit = [0, 16, 24, 32]
  energy = [0, 1.18e-12, 2.18e-12, 3.13e-12]
  energy = [ele * 0.5 for ele in energy]
  f_energy = interp1d(bit, energy, fill_value='extrapolate', kind='cubic')
  ret = f_energy(n_elem).tolist()
  return ret

def get_register_energy(n_elem):
  bit = [0, 12, 24, 32]
  energy = [0, 1.55e-13, 2.30e-13, 2.70e-13]
  f_energy = interp1d(bit, energy, fill_value='extrapolate', kind='linear')
  ret = f_energy(n_elem).tolist()
  return ret

def get_pipeline_energy(n_elem):
  ret = get_register_energy(n_elem)
  return ret

def get_mem_read_energy(n_elem, mem_byte_width):
  num_access = math.ceil(n_elem / mem_byte_width)
  ret = 1.34e-11 * num_access
  return ret

def get_mem_write_energy(n_elem, mem_byte_width):
  num_access = math.ceil(n_elem / mem_byte_width)
  ret = 1.97e-11 * num_access
  return ret

