from policyengine_us.model_api import *


class nc_tanf_household_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "NC TANF household size excludes SSI recipients"
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/wf-114_1-2-2024.pdf#page=2"
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        ssi_income = spm_unit.members("ssi", period)

        # Eligible members are those with no SSI income
        eligible_members = ssi_income <= 0

        return eligible_members.sum()
