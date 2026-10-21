from policyengine_us.model_api import *


class oh_qualifying_capital_gain(Variable):
    value_type = float
    entity = Person
    label = "Ohio qualifying capital gain"
    documentation = (
        "Capital gain from the sale of an interest in an entity that meets "
        "R.C. 5747.79(A)(1): the seller materially participated in the entity "
        "or made a venture capital investment of at least one million dollars "
        "in it, and the entity was organized and headquartered in Ohio for the "
        "five years before the sale."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.79"
    defined_for = StateCode.OH
