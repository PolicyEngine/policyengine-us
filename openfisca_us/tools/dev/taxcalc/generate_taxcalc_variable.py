from matplotlib import units
import yaml
from openfisca_us.model_api import *
from openfisca_core.taxbenefitsystems import TaxBenefitSystem

def create_taxcalc_alias(name: str, variable: Type[Variable]):
    """Creates a new OpenFisca variable with the same metadata as the given variable, but the Tax-Calculator name. 
    The variable will be cast to tax unit level if it is not already.

    Args:
        name (str): The name of the equivalent Tax-Calculator variable.
        variable (Type[Variable]): The OpenFisca-US variable class.
    """

    full_name = "taxcalc_" + name

    def formula(tax_unit, period, parameters):
        if variable.entity == TaxUnit:
            return tax_unit(variable.__name__, period)
        elif variable.entity == Person:
            return add(tax_unit, period, [variable.__name__])
        else:
            raise ValueError("Unsupported entity: {}".format(variable.entity))
            
    return type(
        full_name,
        (Variable,),
        dict(
            entity = TaxUnit,
            definition_period = YEAR,
            label = variable.label + " (Tax-Calculator)",
            unit = variable.unit,
            documentation = variable.documentation + ". This is a read-only variable alias returning the OpenFisca-US variable " + name + " under the (prefixed) name for its equivalent in Tax-Calculator, " + full_name + ".",
            value_type = variable.value_type,
            formula = formula,
        )
    )



def add_taxcalc_variable_aliases(system: TaxBenefitSystem):
    """Adds aliases for all Tax-Calculator variables to the given TaxBenefitSystem.

    Args:
        system (TaxBenefitSystem): The TaxBenefitSystem to which the aliases should be added.
    """

    with open(Path(__file__).parent / "variable_mapping.yaml") as f:
        variable_map = yaml.load(f, Loader=yaml.FullLoader)
    
    for openfisca_us_name, taxcalc_name in variable_map.items():
        system.add_variable(
            create_taxcalc_alias(taxcalc_name, type(system.variables[openfisca_us_name]))
        )

