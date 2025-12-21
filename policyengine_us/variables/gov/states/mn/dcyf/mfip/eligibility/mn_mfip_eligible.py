from policyengine_us.model_api import *


class mn_mfip_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Minnesota MFIP"
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/142G.11"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        # Per MN Stat. 142G.11:
        # Must meet demographic, income, resource, and immigration requirements.
        demographic = spm_unit("is_demographic_tanf_eligible", period)
        income = spm_unit("mn_mfip_income_eligible", period)
        resources = spm_unit("mn_mfip_resources_eligible", period)
        immigration = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        return demographic & income & resources & immigration
