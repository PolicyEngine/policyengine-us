from openfisca_us.model_api import *


class ssi(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Supplemental Security Income"
    label = "Supplemental Security Income"
    unit = USD

    def formula(person, period, parameters):
        eligible = person("is_ssi_eligible", period)
        # If the spouse is eligible, calculate as a couple.
        is_spouse_eligible = person("is_spouse_ssi_eligible", period)
        amounts = parameters(period).ssi.amount
        amount = where(is_spouse_eligible, amounts.couple, amounts.individual)
        countable_income = person("ssi_countable_income", period)
        return (
            eligible
            * max_(amount - countable_income, 0)
            / where(is_spouse_eligible, 2, 1)
        )
