from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_az_dependent_credit() -> Reform:
    class az_dependent_tax_credit_potential(Variable):
        value_type = float
        entity = TaxUnit
        label = "Arizona dependent tax credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.AZ

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            p_base = parameters(
                period
            ).gov.states.az.tax.income.credits.dependent_credit
            p = parameters(period).gov.contrib.states.az.dependent_credit
            dependent = person("is_tax_unit_dependent", period)
            age = person("age", period)
            if p.age_limit.in_effect:
                eligible = dependent & (age < p.age_limit.threshold)
            else:
                eligible = dependent
            per_dependent = where(p.amount < 0, p_base.amount.calc(age), p.amount)
            amount = tax_unit.sum(per_dependent * eligible)
            income = tax_unit("adjusted_gross_income", period)
            filing_status = tax_unit("filing_status", period)
            reduction_start = p_base.reduction.start[filing_status]
            excess = max_(income - reduction_start, 0)
            increments = np.ceil(excess / p_base.reduction.increment)
            reduction_percentage = min_(increments * p_base.reduction.percentage, 1)
            return amount * (1 - reduction_percentage)

    class reform(Reform):
        def apply(self):
            self.update_variable(az_dependent_tax_credit_potential)

    return reform


def create_az_dependent_credit_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_az_dependent_credit()

    p = parameters.gov.contrib.states.az.dependent_credit

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_az_dependent_credit()
    else:
        return None


az_dependent_credit_reform = create_az_dependent_credit_reform_fn(
    None, None, bypass=True
)
