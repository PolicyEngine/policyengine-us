from policyengine_us.model_api import *


class tx_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP eligible"
    documentation = (
        "Determines overall eligibility for Texas LIHEAP assistance"
    )
    reference = "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Check income eligibility
        income_eligible = spm_unit("tx_liheap_income_eligible", period)
        
        # Check categorical eligibility (through SNAP, TANF, or SSI)
        # Need to get a month from the year period to check categorical eligibility
        categorical_eligible = spm_unit("tx_liheap_categorical_eligible", period.first_month)

        # Check if household has utility expenses
        has_utility_expense = spm_unit("utility_expense", period) > 0

        # Eligible if either income eligible OR categorically eligible, AND has utility expenses
        return (income_eligible | categorical_eligible) & has_utility_expense
