from openfisca_us.model_api import *


class md_state_retirement_pickup(Variable):
    value_type = float
    entity = Person
    label = "MD State Retirement Pickup"
    unit = USD
    documentation = "Line 3. STATE RETIREMENT PICKUP. Contributions of a State retirement or pension system pickup amount will be stated separately on your W-2 form (Box 14). The tax on this portion of your wages is deferred for federal but not for state purposes."
    definition_period = YEAR
    default_value = 0.0
