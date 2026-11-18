from policyengine_us.model_api import *


class ssi_income_deemed_from_ineligible_spouse(Variable):
    value_type = float
    entity = Person
    label = "SSI income (deemed from ineligible spouse)"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/20/416.1163"
    documentation = (
        "Annual income deemed from an ineligible spouse, summing each month's "
        "combined countable income less the claimant's own countable income. "
        "Supplied annual amounts retain their annual units."
    )
    defined_for = "is_ssi_aged_blind_disabled"
    unit = USD

    def formula(person, period, parameters):
        return add(person, period, ["ssi_income_deemed_from_ineligible_spouse_monthly"])
