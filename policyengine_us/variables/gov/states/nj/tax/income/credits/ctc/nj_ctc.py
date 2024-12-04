from policyengine_us.model_api import *


class nj_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-4-17-1/"
        "https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2021/1040i.pdf#page=44"
        "https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2022/1040i.pdf#page=44"
        "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=46"
    )
    defined_for = "nj_ctc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.credits.ctc

        # Get amount per qualifying child based on taxable income.
        taxable_income = tax_unit("nj_taxable_income", period)
        amount_per_qualifying_child = p.amount.calc(taxable_income)

        # Get the number of eligible children dependents
        person = tax_unit.members
        age_eligible = person("age", period) < p.age_limit
        dependent = person("is_tax_unit_dependent", period)
        age_eligible_dependent = age_eligible & dependent
        count_eligible = tax_unit.sum(age_eligible_dependent)

        # Calculate total child tax credit
        return count_eligible * amount_per_qualifying_child
