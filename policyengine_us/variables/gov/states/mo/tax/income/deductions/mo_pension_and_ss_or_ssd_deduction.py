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

        #Section C, SS or SSD Amounts
        #We start with section C because, in situations where someone receives both a pension and taxable
        #Social Security, Section A requires information from Section C to be completed.
        eligible_ss_or_ssd = tax_unit('mo_pension_and_ss_or_ssd_section_c', period)

        #Section A, Public Pension Amounts
        #need section c finished to get to this part
        ###requires extra logic from Public Pension Calculation, Line 8: https://dor.mo.gov/forms/MO-1040%20Instructions_2021.pdf#page=17
        #TODO:
        #needs additional logic to account for each individuals share of taxable social security being accounted for separately
        #unclear reference to "See instructions if Line 3 of Section C is more than $0" here: https://dor.mo.gov/forms/MO-A_2021.pdf#page=3
        total_public_pensions = tax_unit('mo_pension_and_ss_or_ssd_section_a', period)

        # Section B, Private Pension Amounts
        total_private_pensions =  tax_unit('mo_pension_and_ss_or_ssd_section_b', period)

        return total_private_pensions + total_public_pensions + eligible_ss_or_ssd
