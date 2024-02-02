from policyengine_us.model_api import *


class or_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oregon Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://olis.oregonlegislature.gov/liz/2023R1/Downloads/MeasureDocument/HB3235/Enrolled"
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        # Get age and dependent status of all people in the tax unit.
        person = tax_unit.members
        age = person("age", period)
        dependent = person("is_tax_unit_dependent", period)
        # Get the number of qualifying dependents in the tax unit.
        p = parameters(period).gov.states["or"].tax.income.credits.ctc
        age_eligible = age < p.ineligible_age
        eligible = age_eligible & dependent
        count_eligible = tax_unit.sum(eligible)
        # Cap the number of qualifying dependents.
        capped_count_eligible = min_(count_eligible, p.child_limit)
        # Get maximum credit amount.
        max_credit = p.amount * capped_count_eligible
        # Get Oregon adjusted gross income.
        or_agi = tax_unit("or_agi", period)
        # Reduce credit amount over the phaseout range.
        excess_agi = max_(or_agi - p.reduction.start, 0)
        percent_reduction = min_(excess_agi / p.reduction.width, 1)
        # Return reduced amount.
        return max_credit * (1 - percent_reduction)
