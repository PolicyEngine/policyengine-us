from policyengine_us.model_api import *


class md_senior_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland Senior Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.marylandtaxes.gov/forms/22_forms/Resident_Booklet.pdf"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = (
            parameters(period)
            .gov.states["md"]
            .tax.income.credits.senior_tax
        )
        agi = person("adjusted_gross_income", period)
        total_agi = tax_unit.sum(agi)
        age_head = tax_unit("age_head", period)
        spouse_age = tax_unit("age_spouse", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        single = filing_status == status.SINGLE
        head_eligible = age_head >= p.age_eligibility
        spouse_eligible = spouse_age >= p.age_eligibility
        both_eligible = head_eligible & spouse_eligible
        eligible = head_eligible | spouse_eligible
        money_eligible = total_agi < p.amount[filing_status]
        single_amount = p.single[filing_status]
        not_single_amount = where(
            both_eligible,
            p.two_aged[filing_status],
            p.one_aged[filing_status]),
        )
        return money_eligible * eligible * where(single, single_amount, not_single_amount)
