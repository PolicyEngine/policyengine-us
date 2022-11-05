from policyengine_us.model_api import *


class mo_itemized_deductions(Variable):
    value_type = float
    entity = Person
    label = "MO Pension and Social Security or SS Disability Deduction"
    unit = USD
    definition_period = YEAR
    reference = ("https://dor.mo.gov/forms/MO-A_2021.pdf#page=3",
    "https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf#page=2",
    "https://revisor.mo.gov/main/OneSection.aspx?section=143.124"
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        mo_agi =  person('mo_adjusted_gross_income', period)
        tax_unit_mo_agi = tax_unit.sum(mo_agi)
        taxable_social_security_benefits = tax_unit("tax_unit_taxable_social_security")
        agi_in_excess_of_taxable_social_security = tax_unit_mo_agi - taxable_social_security_benefits #Equivalent to Line 3 of section A and B
        filing_status = tax_unit('filing_status',period)
        p = parameters(period).gov.states.mo.tax.income.deductions
        ss_or_ssd_allowance = p.ss_or_ssd_deduction_allowance[filing_status]
        agi_over_ss_or_ssd_allowance = max(agi_in_excess_of_taxable_social_security - ss_or_ssd_allowance, 0) #different from Sections A and B, Line 3, floor at 0.
        ssd_amount = tax_unit("social_security_disability", period)
        ss_or_ssd = max(taxable_social_security_benefits, ssd_amount) #need logic for both of these being present, each spouse can claim one
        eligible_ss_or_ssd = max(ss_or_ssd - agi_over_ss_or_ssd_allowance, 0)
        return eligible_ss_or_ssd
