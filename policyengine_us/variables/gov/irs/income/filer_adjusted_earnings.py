from policyengine_us.model_api import *


class filer_adjusted_earnings(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Filer earned income adjusted for self-employment tax"
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/32#c_2",
        "https://www.law.cornell.edu/uscode/text/26/402#e_3",
        "https://www.irs.gov/publications/p596",
        "https://www.irs.gov/instructions/i1040gi",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.irs.ald.misc
        adjustment = (
            (1 - p.self_emp_tax_adj)
            * p.employer_share
            * person("self_employment_tax", period)
        )
        # Federal-style state credits exclude wages that are not includible
        # in federal gross income. Preserve the existing personal SE-tax
        # adjustment and zero floor, without changing gross earned_income.
        excluded_wages = person("employment_income", period) - person(
            "irs_employment_income", period
        )
        adjusted = max_(
            0, person("earned_income", period) - excluded_wages - adjustment
        )
        is_dependent = person("is_tax_unit_dependent", period)
        return tax_unit.sum(adjusted * ~is_dependent)
