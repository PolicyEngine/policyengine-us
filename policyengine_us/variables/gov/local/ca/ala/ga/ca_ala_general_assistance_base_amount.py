from policyengine_us.model_api import *


class ca_ala_general_assistance_base_amount(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alameda County General Assistance base amount"
    definition_period = MONTH
    defined_for = "ca_ala_general_assistance_eligible_person"
    reference = "https://www.alamedacountysocialservices.org/acssa-assets/PDF/GA-Policies/GA-Regulations.pdf#page=28"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.ala.general_assistance.amount
        eligible_persons = spm_unit.members(
            "ca_ala_general_assistance_eligible_person", period
        )
        num_eligible = spm_unit.sum(eligible_persons)
        return where(num_eligible == 2, p.married, p.single)
