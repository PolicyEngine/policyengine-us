from policyengine_us.model_api import *


class nj_other_retirement_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey Other Retirement Income Exclusion"
    unit = USD
    documentation = "New Jersey other retirement income exclusion"
    definition_period = YEAR
    reference = (
        "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21",
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-6-15/",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # follows Worksheet D
        p = parameters(period).gov.states.nj.tax.income.exclusions.retirement

        # determine age eligibility for head and spouse
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        age_eligible = person("age", period) >= p.age_threshold
        age_eligible_unit = tax_unit.sum(age_eligible & (is_head | is_spouse))

        # calculate age-eligible pension income
        pension = person("nj_eligible_pension_income", period)
        pension_income = tax_unit.sum(age_eligible * pension)

        fraction = tax_unit("nj_retirement_exclusion_fraction", period)
        filing_status = tax_unit("filing_status", period)
        exclusion_cap = p.max_amount[filing_status]

        # calculate maximum exclusion
        total_income_person = age_eligible * person("nj_total_income", period)
        total_income = tax_unit.sum(total_income_person)
        maximum_exclusion = min_(fraction * total_income, exclusion_cap)

        # calculate unused pension exclusion
        used = min_(pension_income * fraction, exclusion_cap)
        unused_exclusion = max_(0, maximum_exclusion - used)

        # calculate earnings eligibility
        earnings = add(tax_unit, period, ["earned_income"])
        limit = p.other_retirement_income.earned_income_threshold
        earnings_eligible = earnings <= limit

        # return unused exclusion if age and earnings eligible
        return age_eligible_unit * earnings_eligible * unused_exclusion
