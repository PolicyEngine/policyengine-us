from policyengine_us.model_api import *


class ca_ala_general_assistance_base_amount(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alameda County General Assistance base amount"
    definition_period = MONTH
    defined_for = "in_ala"
    reference = "https://www.alamedacountysocialservices.org/our-services/Work-and-Money/General-Assistance/index"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.ala.general_assistance.amount
        eligible_persons = spm_unit.members(
            "ca_ala_general_assistance_eligible_person", period
        )
        num_eligible = spm_unit.sum(eligible_persons)
        # Determine if this is a couple case (2 eligible adults)
        is_couple_case = num_eligible == 2
        base_amount = where(
            is_couple_case,
            p.married,
            p.single,
        )
        # Only return amount if at least one person is eligible
        return where(num_eligible > 0, base_amount, 0)
