from policyengine_us.model_api import *


class tx_liheap_high_energy_burden(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP household has high energy burden"
    documentation = "Determines if household's energy costs exceed the threshold percentage of income"
    reference = "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.liheap

        # Get household income and utility expenses
        income = spm_unit("household_income", period)
        utility_expense = spm_unit("utility_expense", period)

        # Calculate energy burden ratio
        # Use where to avoid division by zero
        energy_burden = where(income > 0, utility_expense / income, 0)

        # Check if energy burden exceeds threshold
        return energy_burden >= p.high_energy_burden_threshold
