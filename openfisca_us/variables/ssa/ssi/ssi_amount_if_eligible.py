from openfisca_us.model_api import *


class ssi_amount_if_eligible(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = (
        "Supplemental Security Income amount if someone is eligible"
    )
    label = "SSI amount if eligible"
    unit = USD

    def formula(person, period, parameters):
        return (
            person.has_valid_ssi_income
            and person.has_valid_ssi_income_credits
            and person.has_valid_ssi_income_and_credits
        ) * parameters(period).ssi.amount
