from policyengine_us.model_api import *


class eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for EITC"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#c_1_A"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        has_child = tax_unit("tax_unit_children", period) > 0
        age = person("age", period)
        p = parameters(period).gov.irs.credits.eitc
        age_limit = p.eligibility.age
        meets_age_min = age >= age_limit.min
        meets_age_max = age <= age_limit.max
        meets_age_requirements = meets_age_min & meets_age_max
        no_loss_capital_gains = max_(
            0,
            add(tax_unit, period, ["capital_gains"]),
        )
        eitc_investment_income = (
            add(
                tax_unit,
                period,
                ["net_investment_income", "tax_exempt_interest_income"],
            )
            # Replace limited-loss capital gains with no-loss capital gains.
            - tax_unit("c01000", period)  # Limited-loss capital gains.
            + no_loss_capital_gains
        )
        inv_income_disqualified = (
            eitc_investment_income > p.phase_out.max_investment_income
        )
        eligible = has_child | tax_unit.any(meets_age_requirements)
        return eligible & ~inv_income_disqualified
