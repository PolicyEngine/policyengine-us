from policyengine_us.model_api import *


def create_repeal_dependent_exemption() -> Reform:
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


def create_repeal_dependent_exemption_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_repeal_dependent_exemption()

    p = parameters(period).gov.contrib.treasury

    if p.repeal_dependent_exemption:
        return create_repeal_dependent_exemption()
    else:
        return None


repeal_dependent_exemption = create_repeal_dependent_exemption_reform(
    None, None, bypass=True
)
