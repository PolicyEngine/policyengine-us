from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ecpa_adult_dependent_credit() -> Reform:
    class ecpa_adult_dependent_credit(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        unit = USD
        label = "End Child Poverty Act Adult Dependent Credit"

        def formula_2022(tax_unit, period, parameters):
            person = tax_unit.members
            p = parameters(
                period
            ).gov.contrib.congress.tlaib.end_child_poverty_act.adult_dependent_credit
            # Adult dependent credit.
            dependent = person("is_tax_unit_dependent", period)
            adult = person("age", period) >= p.min_age
            return p.amount * tax_unit.sum(adult & dependent)

    class reform(Reform):
        def apply(self):
            self.update_variable(ecpa_adult_dependent_credit)



    return reform


def create_ecpa_adult_dependent_credit_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ecpa_adult_dependent_credit()

    p = parameters(
        period
    ).gov.contrib.congress.tlaib.end_child_poverty_act.adult_dependent_credit

    if p.amount > 0:
        return create_ecpa_adult_dependent_credit()
    else:
        return None


ecpa_adult_dependent_credit = create_ecpa_adult_dependent_credit_reform(
    None, None, bypass=True
)
