from policyengine_us.model_api import *


class mo_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO Pension and Social Security or SS Disability Deduction"
    unit = USD
    definition_period = YEAR
    reference = ("https://dor.mo.gov/forms/MO-A_2021.pdf#page=3",
    "https://dor.mo.gov/forms/MO-1040%20Fillable%20Calculating_2021.pdf#page=2",
    "https://revisor.mo.gov/main/OneSection.aspx?section=143.124"
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        #variables and params needed for all sections
        mo_agi =  person('mo_adjusted_gross_income', period)
        tax_unit_mo_agi = tax_unit.sum(mo_agi)
        taxable_social_security_benefits = tax_unit("tax_unit_taxable_social_security")
        agi_in_excess_of_taxable_social_security = tax_unit_mo_agi - taxable_social_security_benefits #Equivalent to Line 3 of section A and B
        filing_status = tax_unit('filing_status',period)
        p = parameters(period).gov.states.mo.tax.income.deductions

        private_pension_allowance = p.mo_private_pension_deduction_allowance[filing_status]
        agi_over_private_pension_allowance = max(agi_in_excess_of_taxable_social_security - private_pension_allowance, 0)
        private_pension_amount = tax_unit("pension_income", period)
        max_private_pension_amount = p.mo_max_private_pension
        private_pension_value = min(private_pension_amount, max_private_pension_amount)
        total_private_pensions =  max(private_pension_value - agi_over_private_pension_allowance, 0)

        return total_private_pensions