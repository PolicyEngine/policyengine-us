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
        mo_agi =  person('mo_adjusted_gross_income', period)
        tax_unit_mo_agi = tax_unit.sum(mo_agi)
        taxable_social_security_benefits = tax_unit("tax_unit_taxable_social_security")
        agi_in_excess_of_taxable_social_security = tax_unit_mo_agi - taxable_social_security_benefits #Equivalent to Line 3 of section A and B
        filing_status = tax_unit('filing_status',period)
        p = parameters(period).gov.states.mo.tax.income.deductions

        #Section A, Public Pension Amounts
        #need section c finished to get to this part
        ###requires extra logic from Public Pension Calculation, Line 8: https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf#page=17
        #TODO:
        #needs additional logic to account for each individuals share of taxable social security being accounted for separately
        #unclear reference to "See instructions if Line 3 of Section C is more than $0" here: https://dor.mo.gov/forms/MO-A_2021.pdf#page=3

        public_pension_allowance = p.mo_public_pension_deduction_allowance[filing_status]
        agi_over_public_pension__allowance = max(agi_in_excess_of_taxable_social_security - public_pension_allowance,0)
        public_pension_amount = tax_unit("public_pension_income", period)
        max_social_security_benefit = p.mo_max_social_security_benefit # Seen on Line 7, Section A
        public_pension_value = min(public_pension_amount, max_social_security_benefit)
        ss_or_ssdi_exemption_threshold = p.mo_ss_or_ssdi_exemption_threshold[filing_status]

        ssd_amount = tax_unit("social_security_disability", period)
        ss_or_ssd = max(taxable_social_security_benefits, ssd_amount) 
        eligible_ss_or_ssd = person('mo_pension_and_ss_or_ssd_section_c', period)
        

        #From instructions here: https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf#page=17
        adjusted_ss_or_ssdi_value = where((ss_or_ssd - ss_or_ssdi_exemption_threshold) > 0,
            eligible_ss_or_ssd,
            ss_or_ssd,)
      
        ss_less_public_pension_allowance = max(adjusted_ss_or_ssdi_value - public_pension_value, 0)
        total_public_pensions = ss_less_public_pension_allowance - agi_over_public_pension__allowance

        return total_public_pensions