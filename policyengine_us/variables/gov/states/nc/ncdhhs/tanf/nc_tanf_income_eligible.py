from policyengine_us.model_api import *


class nc_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "North Carolina TANF income eligible"
    definition_period = YEAR
    defined_for = "nc_demographic_tanf_eligible"

    def formula(spm_unit, period, parameters):
        monthly_allowed_difference = parameters(
            period
        ).gov.states.nc.ncdhhs.tanf.need_standard.average_reduced_need_standard_thresold
        household_size = spm_unit("nc_tanf_household_size", period)
        reduced_need_standard = spm_unit(
            "nc_tanf_reduced_need_standard", period
        )

        need_standard_fraction = reduced_need_standard / household_size
        difference_threshold = monthly_allowed_difference * MONTHS_IN_YEAR

        return need_standard_fraction >= difference_threshold
