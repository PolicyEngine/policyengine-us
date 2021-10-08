"""
This sub-package is used to define reforms.

A reform is a set of modifications to be applied to a reference tax and benefit system to carry out experiments.

See https://openfisca.org/doc/key-concepts/reforms.html
"""
from openfisca_us.reforms.tools.parametric import (
    parametric_reform,
    reform_from_file,
    set_parameter,
)

from openfisca_us.reforms.tools.structural import (
    new_variable,
    restructure,
    abolish,
)
