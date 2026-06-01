from policyengine_us.model_api import *


class ca_oc_general_relief_other_real_estate_equity(Variable):
    value_type = float
    entity = SPMUnit
    label = "Orange County General Relief other real estate equity"
    documentation = (
        "Uses available household other-real-estate equity. PolicyEngine does "
        "not identify secondary real property that the unit is making a good "
        "faith effort to sell."
    )
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
    defined_for = "in_oc"

    def formula(spm_unit, period, parameters):
        return spm_unit.household("household_other_real_estate_equity", period)
