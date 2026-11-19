from policyengine_us.model_api import *


class StateDeductionMethod(Enum):
    STANDARD = "Standard deduction"
    ITEMIZED = "Itemized deductions"
    AUTOMATIC = "State's usual calculation"


class state_deduction_method(Variable):
    value_type = Enum
    possible_values = StateDeductionMethod
    default_value = StateDeductionMethod.AUTOMATIC
    entity = TaxUnit
    label = "State deduction method"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        if (
            period.start.year == 2025
            and parameters(period).gov.simulation.joint_federal_state_itemization
        ):
            choices = tax_unit("tax_unit_joint_itemization", period)
            return choices % len(StateDeductionMethod)
        return np.full(tax_unit.count, StateDeductionMethod.AUTOMATIC.index)
