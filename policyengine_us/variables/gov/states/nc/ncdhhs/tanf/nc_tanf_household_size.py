from policyengine_us.model_api import *


class nc_tanf_household_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "NC TANF household size excludes SSI recipients"
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        ssi_income = spm_unit.members("ssi", period)

        # Eligible members are those with no SSI income
        eligible_members = ssi_income <= 0

        return eligible_members.sum()
