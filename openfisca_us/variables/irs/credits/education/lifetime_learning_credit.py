from openfisca_us.model_api import *


class lifetime_learning_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Lifetime Learning Credit"
    unit = "currency-USD"
    documentation = "Value of the non-refundable Lifetime Learning Credit"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/25A#c"

    def formula(tax_unit, period, parameters):
        education = parameters(period).irs.credits.education
        llc = education.lifetime_learning_credit
        is_aoc_eligible = tax_unit.members(
            "is_eligible_for_american_opportunity_credit", period
        )
        eligible_expenses = tax_unit.sum(
            tax_unit.members("qualified_tuition_expenses", period)
            * ~is_aoc_eligible
        )
        capped_expenses = min_(llc.expense_limit, eligible_expenses)
        maximum_amount = llc.rate * capped_expenses
        agi = tax_unit("adjusted_gross_income", period)
        is_joint = tax_unit("tax_unit_is_joint", period)
        phaseout_start = where(
            is_joint,
            education.phaseout.start.single,
            education.phaseout.start.joint,
        )
        excess_agi = max(0, agi - phaseout_start)
        percentage_reduction = excess_agi / maximum_amount
        return max_(0, maximum_amount * (1 - percentage_reduction))
