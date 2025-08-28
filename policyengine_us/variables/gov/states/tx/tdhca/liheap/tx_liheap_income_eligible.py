from policyengine_us.model_api import *


class tx_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP income eligible"
    documentation = "Determines if household meets Texas LIHEAP income eligibility requirements"
    reference = "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.liheap
        
        # Get household monthly income (average over the year)
        monthly_income = spm_unit("tx_liheap_income", period.first_month)
        annual_income = monthly_income * 12

        # Get household size
        size = spm_unit.nb_persons()

        # Get FPG (Federal Poverty Guidelines) for household
        fpg = spm_unit("spm_unit_fpg", period)

        # Apply Texas FPG ratio (150%)
        income_limit = fpg * p.income_limit_fpg_ratio

        return annual_income <= income_limit
