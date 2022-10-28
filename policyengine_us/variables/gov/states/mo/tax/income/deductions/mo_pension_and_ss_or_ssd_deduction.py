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

        #public pension calculation

        #mo_agi - taxable_social_security_benefits #both on tax_unit level
        person = tax_unit.members
        mo_agi =  person('mo_adjusted_gross_income', period)
        tax_unit_mo_agi = tax_unit.sum(mo_agi)

        taxable_social_security_benefits = tax_unit("tax_unit_taxable_social_security")

        agi_in_excess_of_taxable_social_security = tax_unit_mo_agi - taxable_social_security_benefits
        #create param for allowance amount based on filing status
        filing_status = tax_unit('filing_status',period)
        p = parameters(period).gov.states.mo.tax.income.deductions
        
        public_pension_allowance = p.mo_public_pension_deduction_allowance[filing_status]
        private_pension_allowance = p.mo_private_pension_deduction_allowance[filing_status]
        ss_or_ssd_allowance = p.ss_or_ssd_deduction_allowance[filing_status]

        agi_over_public_pension__allowance = max(agi_in_excess_of_taxable_social_security - public_pension_allowance,0)
        agi_over_private_pension__allowance = max(agi_in_excess_of_taxable_social_security - private_pension_allowance,0)
        agi_over_ss_or_ssd__allowance = max(agi_in_excess_of_taxable_social_security - ss_or_ssd_allowance,0)

        public_pension_amount = tax_unit("public_pension_income", period)
        private_pension_amount = tax_unit("private_pension_income", period)
        ssd_amount = tax_unit("social_security_disability", period)

        max_social_security_benefit = p.mo_max_social_security_benefit
        max_private_pension_amount = p.mo_max_private_session

        #Section C, SS or SSD Amounts
        ss_or_ssd = max(taxable_social_security_benefits, ssd_amount)
        total_ss_or_ssd = ss_or_ssd - agi_over_ss_or_ssd__allowance
        
        #Section A, Public Pension Amounts
        #need section c finished to get to this part
        ###requires extra logic from: https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf#page=17
        public_pension_value = min(public_pension_amount,max_social_security_benefit)
        ss_less_public_pension_allowance = max(ss_or_ssd - public_pension_value, 0)
        total_public_pensions = ss_less_public_pension_allowance - agi_over_public_pension__allowance

        # Section B, Private Pension Amounts
        private_pension_value = min(private_pension_amount,max_social_security_benefit)
        ss_less_private_pension = max(ss_or_ssd - private_pension_value, 0)
        total_private_pensions = ss_less_private_pension - agi_over_private_pension__allowance


        #if (mo_agi-taxable_social_security_benefits) - allowance > 0:
        #
        # calculate taxable pension from each spouse
        # then store taxable pension or max social security amount, whichever is less
        # if taxable social security was recieved subtract to line above, with a floor at 0
        # subtract (mo_agi-taxable_social_security_benefits) from the line above, with a floor at 0