# energy table
def get_energy(name, nbits):
  if name == "__add__":
    ret = get_add_energy(nbits)
  elif name == "__sub__":
    ret = get_sub_energy(nbits)
  elif name == "__mul__":
    ret = get_mul_energy(nbits)
  else:
    ret = 0
  return ret

def get_add_energy(nbits):
  # dummy energy
  ret = 1 * nbits
  return ret

def get_sub_energy(nbits):
  # dummy energy
  ret = 2 * nbits
  return ret

def get_mul_energy(nbits):
  # dummy energy
  ret = 4 * nbits
  return ret
