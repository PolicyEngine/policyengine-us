from matplotlib import units
import yaml
from policyengine_us.model_api import *
from policyengine_core.taxbenefitsystems import TaxBenefitSystem


def import_yaml():
    import yaml

    try:
        from yaml import CLoader as Loader
    except ImportError:
        from yaml import SafeLoader as Loader
    return yaml, Loader


yaml, Loader = import_yaml()


def create_taxcalc_alias(name: str, variable: Type[Variable]):
    """Creates a new OpenFisca variable with the same metadata as the given variable, but the Tax-Calculator name.
    The variable will be cast to tax unit level if it is not already.

    Args:
        name (str): The name of the equivalent Tax-Calculator variable.
        variable (Type[Variable]): The PolicyEngine US variable class.
    """

    full_name = "taxcalc_" + name

    def formula(tax_unit, period, parameters):
        if variable.entity == TaxUnit:
            return tax_unit(variable.__name__, period)
        elif variable.entity == Person:
            return add(tax_unit, period, [variable.__name__])
        elif variable.entity == Household:
            return tax_unit.value_from_first_person(
                tax_unit.members.household(variable.__name__, period)
            )
        else:
            raise ValueError("Unsupported entity: {}".format(variable.entity))

    original_documentation = (
        variable.documentation if hasattr(variable, "documentation") else None
    )
    addition_to_documentation = (
        "This is a read-only variable alias returning the PolicyEngine US variable "
        + name
        + " under the (prefixed) name for its equivalent in Tax-Calculator, "
        + full_name
        + "."
    )
    documentation = (
        original_documentation + ". " + addition_to_documentation
        if original_documentation
        else addition_to_documentation
    )

    return type(
        full_name,
        (Variable,),
        dict(
            entity=TaxUnit,
            definition_period=YEAR,
            label=variable.label + " (Tax-Calculator)"
            if hasattr(variable, "label")
            else name + "(Tax-Calculator)",
            unit=variable.unit if hasattr(variable, "unit") else None,
            documentation=documentation,
            value_type=variable.value_type,
            formula=formula,
        ),
    )


def add_taxcalc_variable_aliases(system: TaxBenefitSystem):
    """Adds aliases for all Tax-Calculator variables to the given TaxBenefitSystem.

    Args:
        system (TaxBenefitSystem): The TaxBenefitSystem to which the aliases should be added.
    """

    with open(Path(__file__).parent / "variable_mapping.yaml") as f:
        variable_map = yaml.load(f, Loader=Loader)

    for policyengine_us_name, taxcalc_name in variable_map.items():
        try:
            system.add_variable(
                create_taxcalc_alias(
                    taxcalc_name, type(system.variables[policyengine_us_name])
                )
            )
        except Exception as e:
            print(
                "Error adding alias for {}: {}".format(policyengine_us_name, e)
            )
            raise e
