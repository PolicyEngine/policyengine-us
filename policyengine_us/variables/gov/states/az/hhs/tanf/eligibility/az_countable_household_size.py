from policyengine_us.model_api import *


class az_countable_household_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Arizona Cash Assistance Countable Household Size"
    definition_period = YEAR
    defined_for: StateCode.AZ

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.hhs.tanf.eligibility.payment_standard
        size = spm_unit("spm_unit_size", period)
        return min_(size, p.max_household_size)
