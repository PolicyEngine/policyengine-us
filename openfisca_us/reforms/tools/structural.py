from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from typing import Union


def abolish(variable: Union[type, str]) -> Reform:
    if isinstance(variable, type):
        variable = variable.__name__

    class reform(Reform):
        def apply(self):
            self.neutralize_variable(variable)

    return reform


def restructure(variable_class: type) -> Reform:
    class reform(Reform):
        def apply(self):
            self.update_variable(variable_class)

    return reform


def new_variable(variable_class: type) -> Reform:
    class reform(Reform):
        def apply(self):
            self.add_variable(variable_class)

    return reform
