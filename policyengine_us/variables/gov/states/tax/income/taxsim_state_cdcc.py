from policyengine_us.model_api import *


class taxsim_state_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "State child and dependent care tax credit"
    documentation = (
        "Sum the state child and dependent care credit components configured "
        "for the year. Each component retains its own treatment of tax "
        "liability limits."
    )
    unit = USD
    definition_period = YEAR
    adds = "gov.states.household.state_cdccs"
