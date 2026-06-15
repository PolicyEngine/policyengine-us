from policyengine_us.model_api import *


class ca_sf_caap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for San Francisco County CAAP due to income"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(spm_unit, period, parameters):
        # We don't track the applicant-vs-recipient gross/net income-test split
        # at the moment; net income below the max grant is applied uniformly
        # (SEC. 20.7-10).
        countable_income = spm_unit("ca_sf_caap_countable_income", period)
        max_grant = spm_unit("ca_sf_caap_max_grant", period)
        return countable_income < max_grant
