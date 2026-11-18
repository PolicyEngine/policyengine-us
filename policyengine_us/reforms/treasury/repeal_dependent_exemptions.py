from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


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
            # Only the filers' own exemptions remain; a filer who can be
            # claimed as a dependent has none (IRC 151(d)(2)).
            dependent_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
            independent_filers = tax_unit(
                "head_spouse_count_not_dependent_elsewhere", period
            )
            return where(
                dependent_filer, independent_filers, total_unit_size - dependents
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(exemptions_count)

    return reform


def create_repeal_dependent_exemptions_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_repeal_dependent_exemptions()

    p = parameters.gov.contrib.treasury

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).repeal_dependent_exemptions:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_repeal_dependent_exemptions()
    else:
        return None


repeal_dependent_exemptions = create_repeal_dependent_exemptions_reform(
    None, None, bypass=True
)
