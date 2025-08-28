from policyengine_us.model_api import *


class tx_liheap_crisis_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP crisis benefit"
    unit = USD
    documentation = "Crisis LIHEAP benefit amount"
    reference = "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.liheap

        # Check crisis eligibility
        crisis_eligible = spm_unit("tx_liheap_crisis_eligible", period)

        # Get utility expenses as proxy for crisis amount needed
        utility_expense = spm_unit("utility_expense", period)

        # Crisis benefit is limited to actual need or maximum
        crisis_amount = min_(utility_expense, p.crisis_maximum_benefit)

        # Return crisis benefit only if crisis eligible
        return where(crisis_eligible, crisis_amount, 0)
