from policyengine_us.model_api import *


class nc_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "North Carolina TANF income eligible"
    definition_period = YEAR
    defined_for = "nc_demographic_tanf_eligible"
    reference = (
        "https://www.ncdhhs.gov/efs-wf-06-2025a2/open#page=19",
        "https://policies.ncdhhs.gov/wp-content/uploads/wf-114_1-2-2024.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.tanf
        household_size = spm_unit("nc_tanf_household_size", period)
        reduced_need_standard = spm_unit("nc_tanf_reduced_need_standard", period)
        # State Plan Financial Rules 8: a family remains eligible if the
        # payment (50% of the difference between countable income and the
        # need standard) is $25 or more.
        payment = reduced_need_standard * p.benefit.payment_percentage
        minimum_payment = (
            p.eligibility.average_reduced_need_standard_threshold * MONTHS_IN_YEAR
        )

        return (household_size > 0) & (payment >= minimum_payment)
