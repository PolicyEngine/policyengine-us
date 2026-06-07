from policyengine_us.model_api import *


class ca_sf_caap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for San Francisco County CAAP"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(spm_unit, period, parameters):
        age_eligible = spm_unit("ca_sf_caap_age_eligible", period)
        property_eligible = spm_unit("ca_sf_caap_personal_property_eligible", period)
        income_eligible = spm_unit("ca_sf_caap_income_eligible", period)
        other_aid_eligible = spm_unit("ca_sf_caap_other_aid_eligible", period)
        # At least one person in the unit must be eligible (not an SSI recipient
        # and with a qualified immigration status).
        budget_unit_size = spm_unit("ca_sf_caap_budget_unit_size", period)
        has_eligible_person = budget_unit_size > 0
        return (
            age_eligible
            & property_eligible
            & income_eligible
            & other_aid_eligible
            & has_eligible_person
        )
