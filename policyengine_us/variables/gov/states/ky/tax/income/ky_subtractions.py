from policyengine_us.model_api import *


class ky_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Kentucky subtractions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53498"
        "https://revenue.ky.gov/Forms/Schedule%20M%202022.pdf#page=1"
        "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=23"
        "https://revenue.ky.gov/Forms/Schedule%20M-2021.pdf#page=1"
        "https://taxsim.nber.org/historical_state_tax_forms/KY/2021/Form%20740%20Packet%20Instructions-2021.pdf#page=27"
    )
    defined_for = StateCode.KY
    adds = "gov.states.ky.tax.income.subtractions"
