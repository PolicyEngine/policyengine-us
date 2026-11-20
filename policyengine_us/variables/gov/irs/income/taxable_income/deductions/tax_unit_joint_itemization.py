from policyengine_us.model_api import *
from policyengine_us.tools.state_itemization import (
    STATE_METHOD_COUNT,
    joint_itemization,
    joint_itemization_is_enabled,
)


class tax_unit_joint_itemization(Variable):
    value_type = int
    entity = TaxUnit
    label = "Joint federal and state deduction election"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        if joint_itemization_is_enabled(period, parameters):
            return joint_itemization(tax_unit, period, parameters)
        return STATE_METHOD_COUNT * tax_unit("tax_unit_itemizes", period) + np.asarray(
            tax_unit("state_deduction_method", period)
        )
