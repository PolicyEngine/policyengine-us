from openfisca_us.model_api import *


class school_meal_paid_daily_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "School meal subsidies per full-price child per day"
    unit = USD
    documentation = "Value of school meal subsidies paid to full-price children per day in household's state"

    def formula(spm_unit, period, parameters):
        # Get state group and tier (based on poverty ratio) for SPM unit.
        state_group = spm_unit.household("state_group_str", period)
        p_amount = parameters(period).gov.usda.school_meals.amount
        nslp_per_child = p_amount.nslp[state_group]["PAID"]
        sbp_per_child = p_amount.sbp[state_group]["PAID"]
        return nslp_per_child + sbp_per_child
