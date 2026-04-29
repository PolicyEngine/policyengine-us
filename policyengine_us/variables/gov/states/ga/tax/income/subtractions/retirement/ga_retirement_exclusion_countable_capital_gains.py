from policyengine_us.model_api import *


class ga_retirement_exclusion_countable_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Countable capital gains (losses) for the Georgia retirement exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.georgia.gov/document/document/2024-it-511-individual-income-tax-booklet/download",  # Schedule 1, Page 2
        "https://www.irs.gov/pub/irs-pdf/f1040sd.pdf",
    )
    defined_for = StateCode.GA

    def formula(person, period, parameters):
        return person("loss_limited_net_capital_gains_person", period)
