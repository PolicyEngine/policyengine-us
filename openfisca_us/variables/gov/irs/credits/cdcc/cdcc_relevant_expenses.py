from openfisca_us.model_api import *


class cdcc_relevant_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC-relevant care expenses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/21#c",
        "https://www.law.cornell.edu/uscode/text/26/21#d_1",
    )

    def formula(tax_unit, period, parameters):
        # First, cap based on the number of eligible care receivers
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        cdcc = parameters(period).irs.credits.cdcc
        count_eligible = min_(
            cdcc.eligibility.max, tax_unit("count_cdcc_eligible", period)
        )
        eligible_capped_expenses = min_(expenses, cdcc.max * count_eligible)
        # Then, cap further to the lowest earnings between the taxpayer and spouse
        person = tax_unit.members
        earned_income = person("earned", period)
        is_joint = tax_unit("tax_unit_is_joint", period)
        is_spouse = person("is_tax_unit_spouse", period)
        is_head = person("is_tax_unit_head", period)
        head_earnings = tax_unit.sum(is_head * earned_income)
        spouse_earnings = tax_unit.sum(is_spouse * earned_income)
        lower_earnings = where(
            is_joint,
            min_(head_earnings, spouse_earnings),
            head_earnings,
        )
        return min_(eligible_capped_expenses, lower_earnings)
