from policyengine_us.model_api import *


class nc_scca_entry_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "North Carolina entry eligibility for Subsidized Child Care Assistance Program"
    )
    reference = (
        "https://policies.ncdhhs.gov/wp-content/uploads/FINAL-Chapter-7-Family-definition-and-determining-income-eligibility-08-05-24.pdf#page=2",
        "https://policies.ncdhhs.gov/wp-content/uploads/Chapter-5-CN-25-3-Establishing-Need-and-Plan-of-Care.pdf#page=2",
    )
    definition_period = MONTH
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        has_eligible_child = add(spm_unit, period, ["nc_scca_child_eligible"]) > 0
        return has_eligible_child & spm_unit("nc_scca_need_eligible", period)
