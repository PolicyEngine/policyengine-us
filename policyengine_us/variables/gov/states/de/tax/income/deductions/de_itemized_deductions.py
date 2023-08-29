from policyengine_us.model_api import *


class de_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=7"
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=11"
        "https://casetext.com/statute/delaware-code/title-30-state-taxes/part-ii-income-inheritance-and-estate-taxes/chapter-11-personal-income-tax/subchapter-ii-resident-individuals/section-1109-itemized-deductions-for-application-of-this-section-see-66-del-laws-c-86-section-8"
    )
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        # ... calculate itemized deductions offset
        p = parameters(period).gov.states.mn.tax.income.deductions
        net_deds = max_(0, itm_deds_less_salt)
        net_deds_offset = p.deduction_fraction * net_deds
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        excess_agi = max_(0, agi - p.agi_threshold[filing_status])
        excess_agi_offset = p.excess_agi_fraction * excess_agi
        offset = min_(net_deds_offset, excess_agi_offset)
        return max_(0, itm_deds_less_salt - offset)
