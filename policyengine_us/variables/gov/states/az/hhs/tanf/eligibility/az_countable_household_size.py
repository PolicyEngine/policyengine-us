from policyengine_us.model_api import *


class az_countable_household_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Arizona Cash Assistance Countable Household Size"
    definition_period = YEAR
    defined_for: "az_hhs_tanf_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.hhs.tanf.eligibility.payment_standard
        unit_size = spm_unit("spm_unit_size", period)
        return min_(unit_size, p.max_household_size)
