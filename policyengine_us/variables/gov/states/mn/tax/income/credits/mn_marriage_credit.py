from policyengine_us.model_api import *


class mn_marriage_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota marriage credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1ma_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1ma_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        mn_itax = parameters(period).gov.states.mn.tax.income
        p = mn_itax.credits.marriage
        # determine filing status eligibility
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        # determine individual income eligibility
        person = tax_unit.members
        income = add(person, period, p.income_sources) - person(
            "self_employment_tax_ald_person", period
        )
        is_head = person("is_tax_unit_head", period)
        head_income = tax_unit.sum(is_head * income)
        is_spouse = person("is_tax_unit_spouse", period)
        spouse_income = tax_unit.sum(is_spouse * income)
        min_income = min_(head_income, spouse_income)
        individual_income_eligible = min_income >= p.minimum_individual_income
        # determine taxable income eligibility
        taxinc0 = tax_unit("mn_taxable_income", period)
        taxable_income_eligible = taxinc0 >= p.minimum_taxable_income
        # determine overall eligibility for credit
        eligible = joint & individual_income_eligible & taxable_income_eligible
        # determine credit amount
        std_ded = mn_itax.deductions.standard.base[filing_status]
        fractional_std_ded = p.standard_deduction_fraction * std_ded
        taxinc1 = max_(0, min_income - fractional_std_ded)
        itax1 = mn_itax.rates.single.calc(taxinc1)
        taxinc2 = max_(0, taxinc0 - taxinc1)
        itax2 = mn_itax.rates.single.calc(taxinc2)
        itax0 = tax_unit("mn_basic_tax", period)
        amount = max_(0, itax0 - itax1 - itax2)
        # capped credit only for eligibles
        return eligible * min_(amount, p.maximum_amount)
