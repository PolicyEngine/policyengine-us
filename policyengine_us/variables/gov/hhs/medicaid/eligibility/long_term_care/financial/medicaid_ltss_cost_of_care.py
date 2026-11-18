from policyengine_us.model_api import *


class medicaid_ltss_cost_of_care(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS cost of care"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Explicit Washington medically needy threshold input. For a medical "
        "institution it is the applicable state-contracted daily rate "
        "multiplied by covered days; for a named HCS waiver it is the "
        "applicable average monthly state nursing-facility rate. It is "
        "trusted rather than derived and does not represent a Medicaid "
        "benefit amount or patient liability."
    )
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1395",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-515-1508",
    )
