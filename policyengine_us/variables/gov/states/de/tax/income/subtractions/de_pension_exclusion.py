from policyengine_us.model_api import *


class de_pension_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware pension exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=6"
        "https://delcode.delaware.gov/title30/c011/sc02/index.html"
    )
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.de.tax.income.subtractions.pension_exclusion
        
        # determine age eligibility
        age_head = tax_unit("age_head", period)
        under_60_head_eligible = (age_head < p.min_age).astype(int)
        above_60_head_eligible = (age_head >= p.min_age).astype(int)

        # determine military eligiblity
        is_military = tax_unit("is_military", period)
        military_eligible = (is_military & under_60_head_eligible).astype(int)

        # determine pension exclusion value based on military status
        exclusion_value = where(military_eligible, p.max_pension_amount_military, p.max_pension_amount_non_military)
        
        # determine pension exclusion amount
        pension_income = tax_unit("taxable_pension_income", period)

        # determine eligible retirement income for head above 60
        elig_retirement_income = tax_unit("eligible_retirement_income", period)
        total_income_above_60 = pension_income + elig_retirement_income

        # determine exclusion eligibility
        is_eligible_for_under_60_military = (under_60_head_eligible & is_military).astype(int)
        is_eligible_for_under_60_non_military = (under_60_head_eligible & ~is_military).astype(int)
        is_eligible_for_above_60 = (above_60_head_eligible).astype(int)

        # apply the exclusion value or the pension income, whichever is lower, for eligible individuals
        pension_exclusion_under_60_military = where(is_eligible_for_under_60_military, min_(exclusion_value, pension_income), 0)
        pension_exclusion_under_60_non_military = where(is_eligible_for_under_60_non_military, min_(exclusion_value, pension_income), 0)
        pension_exclusion_above_60 = where(is_eligible_for_above_60, min_(exclusion_value, total_income_above_60), 0)

        
        return pension_exclusion_under_60_military + pension_exclusion_under_60_non_military + pension_exclusion_above_60