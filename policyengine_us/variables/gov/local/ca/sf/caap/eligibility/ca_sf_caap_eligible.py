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
        # At least one person in the unit must be eligible (not on SSI or CAPI and
        # with a qualified immigration status).
        has_eligible_person = spm_unit("ca_sf_caap_budget_unit_size", period) > 0
        # CalWORKs is a family grant; its recipients are barred from CAAP
        # (SEC. 20.7-6; Manual 91-2). SSI and CAPI are individual programs handled
        # per person in ca_sf_caap_eligible_person; RCA/ECA are also barred but
        # have no PolicyEngine variable at the moment.
        not_on_calworks = spm_unit("ca_tanf", period.this_year) == 0
        return (
            age_eligible
            & property_eligible
            & income_eligible
            & has_eligible_person
            & not_on_calworks
        )
