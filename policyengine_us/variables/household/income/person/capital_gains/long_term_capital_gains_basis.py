from policyengine_us.model_api import *


class long_term_capital_gains_basis(Variable):
    value_type = float
    entity = Person
    label = "long-term capital gains basis"
    unit = USD
    documentation = (
        "Cost basis associated with realized long-term capital gains, "
        "stored for capital-gains basis indexation analysis."
    )
    definition_period = YEAR
    uprating = "calibration.gov.irs.soi.long_term_capital_gains"
