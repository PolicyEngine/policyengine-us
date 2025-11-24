from policyengine_us.model_api import *


class tx_ottanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Texas One-Time TANF (OTTANF)"
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-2421-eligibility-criteria",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-801",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # OTTANF eligibility per A-2421:
        # 1. Must meet all regular TANF eligibility requirements
        #    (child, income, resources, immigration)
        # 2. Must be eligible for TANF grant of $10 or more
        # 3. Must meet one of four crisis criteria

        # Regular TANF eligibility (child, income, resources, immigration)
        regular_tanf_eligible = spm_unit("tx_tanf_eligible", period)

        # Must be eligible for at least $10 grant
        payment_standard = spm_unit("tx_tanf_payment_standard", period)
        countable_income = spm_unit("tx_tanf_countable_income", period)
        potential_grant = payment_standard - countable_income

        p = parameters(period).gov.states.tx.tanf
        eligible_for_min_grant = potential_grant >= p.minimum_grant

        # Crisis criteria (user input)
        crisis = spm_unit("tx_ottanf_crisis_criteria", period)

        return regular_tanf_eligible & eligible_for_min_grant & crisis
