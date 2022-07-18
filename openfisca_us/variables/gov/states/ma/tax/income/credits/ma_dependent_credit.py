from openfisca_us.model_api import *


class ma_dependent_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA dependent credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.mass.gov/info-details/mass-general-laws-c62-ss-6"  # (y)
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.tax.income.credits.dependent
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        child = age < p.child_age_limit
        elderly = age >= p.elderly_age_limit
        disabled = person("is_disabled", period)
        eligible = dependent & (child | elderly | disabled)
        count_eligible = tax_unit.sum(eligible)
        capped_eligible = min_(count_eligible, p.dependent_cap)
        return capped_eligible * p.amount
