"""Chemical Engineering Design Library (ChEDL). Utilities for process modeling.
Copyright (C) 2020 Caleb Bell <Caleb.Andrew.Bell@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


__all__ = ['u']
import types


import chemicals

try:
    from pint import _DEFAULT_REGISTRY as u

except ImportError: # pragma: no cover
    raise ImportError('The unit handling in fluids requires the installation '
                      'of the package pint, available on pypi or from '
                      'https://github.com/hgrecco/pint')
from fluids.units import variable_output_wrapper, wrap_numpydoc_obj, wraps_numpydoc

__pint_wrapped_functions = {}

variable_output_unit_funcs = {
    # True: arg should be present; False: arg should be None
    'speed_of_sound': ({(True, True, True, True, True): [u.m/u.s],
                        (True, True, True, True, False): [u.m*u.kg**0.5/u.s/u.mol**0.5],
                        }, 5),
    'Lastovka_Shaw': ({(True, True, True, False): [u.J/u.kg/u.K],
                      (True, True, False, False): [u.J/u.kg/u.K], # cyclic_aliphatic flag
                      (True, True, True, True): [u.J/u.mol/u.K],
                      (True, True, False, True): [u.J/u.mol/u.K], # cyclic_aliphatic flag
                      }, 4),
    'Lastovka_Shaw_integral_over_T': ({(True, True, True, False): [u.J/u.kg/u.K],
                      (True, True, False, False): [u.J/u.kg/u.K], # cyclic_aliphatic flag
                      (True, True, True, True): [u.J/u.mol/u.K],
                      (True, True, False, True): [u.J/u.mol/u.K], # cyclic_aliphatic flag
                      }, 4),
    'Lastovka_Shaw_integral': ({(True, True, True, False): [u.J/u.kg],
                      (True, True, False, False): [u.J/u.kg], # cyclic_aliphatic flag
                      (True, True, True, True): [u.J/u.mol],
                      (True, True, False, True): [u.J/u.mol], # cyclic_aliphatic flag
                      }, 4),

    'Dadgostar_Shaw': ({(True, True, False): [u.J/u.kg/u.K],
                      (True, True, True): [u.J/u.mol/u.K],
                      }, 3),
    'Dadgostar_Shaw_integral': ({(True, True, False): [u.J/u.kg],
                      (True, True, True): [u.J/u.mol],
                      }, 3),
    'Dadgostar_Shaw_integral_over_T': ({(True, True, False): [u.J/u.kg/u.K],
                      (True, True, True): [u.J/u.mol/u.K],
                      }, 3),

    'Lastovka_solid': ({(True, True, False): [u.J/u.kg/u.K],
                      (True, True, True): [u.J/u.mol/u.K],
                      }, 3),
    'Lastovka_solid_integral': ({(True, True, False): [u.J/u.kg],
                      (True, True, True): [u.J/u.mol],
                      }, 3),
    'Lastovka_solid_integral_over_T': ({(True, True, False): [u.J/u.kg/u.K],
                      (True, True, True): [u.J/u.mol/u.K],
                      }, 3),
    'Rackett_fit': ({(True, True, True, True, True, True): [u.m**3/u.mol],
                  (True, True, True, True, True, False): [u.m**3/u.kg],
                  }, 6),
}

unwrapped_objects = frozenset(['PeriodicTable'])
for name in dir(chemicals):
    if name == '__getattr__' or name == '__test__':
        continue
    obj = getattr(chemicals, name)
    if isinstance(obj, types.FunctionType):
        obj = wraps_numpydoc(u)(obj)
    elif type(obj) == type:
        if obj.__name__ not in unwrapped_objects:
            obj = wrap_numpydoc_obj(obj)
    elif type(obj) is types.ModuleType:
        continue
    elif isinstance(obj, str):
        continue
    if name == '__all__':
        continue
    __all__.append(name)
    __pint_wrapped_functions.update({name: obj})

globals().update(__pint_wrapped_functions)

for name, val in variable_output_unit_funcs.items():
    globals()[name] = variable_output_wrapper(getattr(chemicals, name),
            __pint_wrapped_functions[name], val[0], val[1])
