from policyengine_us.model_api import *
from policyengine_us.reforms.utils import create_reform_if_active


def create_repeal_dependent_exemptions() -> Reform:
    class exemptions_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Number of tax exemptions"
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            total_unit_size = tax_unit("tax_unit_size", period)
            dependents = tax_unit("tax_unit_dependents", period)
            return total_unit_size - dependents

    class reform(Reform):
        def apply(self):
            self.update_variable(exemptions_count)

    return reform


def create_repeal_dependent_exemptions_reform(
    parameters, period, bypass: bool = False
):
    return create_reform_if_active(
        parameters,
        period,
        "gov.contrib.treasury",
        "repeal_dependent_exemptions",
        create_repeal_dependent_exemptions,
        bypass,
    )


repeal_dependent_exemptions = create_repeal_dependent_exemptions_reform(
    None, None, bypass=True
)
