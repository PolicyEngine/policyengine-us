from policyengine_us.model_api import *


class eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for EITC"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/32#c_1_A"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        has_child = tax_unit.any(person("is_child", period))
        age = person("age", period)
        eitc = parameters.gov.irs.credits.eitc(period)
        min_age = parameters.gov.irs.credits.eitc.eligibility.age.min(period)
        meets_age_requirements = (age >= min_age) & (
            age <= eitc.eligibility.age.max
        )
        no_loss_capital_gains = max_(
            0,
            add(
                tax_unit,
                period,
                ["short_term_capital_gains", "long_term_capital_gains"],
            ),
        )
        eitc_investment_income = (
            tax_unit("net_investment_income", period)
            + add(tax_unit, period, ["tax_exempt_interest_income"])
            # replace limited-loss capital gains with no-loss capital gains
            - tax_unit("c01000", period)  # limited-loss capital gains
            + no_loss_capital_gains
        )
        inv_income_disqualified = (
            eitc_investment_income > eitc.phase_out.max_investment_income
        )
        eligible = has_child | tax_unit.any(meets_age_requirements)
        return eligible & ~inv_income_disqualified
