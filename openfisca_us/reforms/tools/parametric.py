import openfisca_us
from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from typing import Union


def set_parameter(
    path: Union[Parameter, str],
    value: float,
    period: str = "year:2015:10",
    return_modifier=False,
) -> Reform:
    if isinstance(path, Parameter):
        path = path.name

    def modifier(parameters: ParameterNode):
        node = parameters
        for name in path.split("."):
            try:
                if "[" not in name:
                    node = node.children[name]
                else:
                    try:
                        name, index = name.split("[")
                        index = int(index[:-1])
                        node = node.children[name].brackets[index]
                    except:
                        raise ValueError(
                            "Invalid bracket syntax (should be e.g. tax.brackets[3].rate"
                        )
            except:
                raise ValueError(
                    f"Could not find the parameter (failed at {name})."
                )
        node.update(period=period, value=value)
        return parameters

    if return_modifier:
        return modifier

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modifier)

    return reform


def change_parameter(
    path: Parameter, value: float, period: str = "year:2015:10"
) -> Reform:
    path = path.name

    def modifier(parameters: ParameterNode):
        node = parameters
        for name in path.split("."):
            try:
                if "[" not in name:
                    node = node.children[name]
                else:
                    try:
                        name, index = name.split("[")
                        index = int(index[:-1])
                        node = node.children[name].brackets[index]
                    except:
                        raise ValueError(
                            "Invalid bracket syntax (should be e.g. tax.brackets[3].rate"
                        )
            except:
                raise ValueError(
                    f"Could not find the parameter (failed at {name})."
                )
        node.update(period=period, value=node.get_at_instant(period))
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modifier)

    return reform


def parametric_reform(modifier_func):
    class reform(Reform):
        def apply(self):
            self.modify_parameters(modifier_func)

    return reform


def reform_from_file(filepath: str):
    def replace_parameters(parameters):
        parameters = load_parameter_file(filepath)
        return parameters

    return parametric_reform(replace_parameters)
