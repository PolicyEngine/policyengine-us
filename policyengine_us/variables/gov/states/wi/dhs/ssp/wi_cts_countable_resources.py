from policyengine_us.model_api import *


class wi_cts_countable_resources(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin CTS individual countable resources"
    definition_period = MONTH
    unit = USD
    quantity_type = STOCK
    # PDF pages 31-32
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=31"
    documentation = "SSI countable resources plus other CTS countable resources. SSI recipients are excluded at the group calculation."

    def formula(person, period, parameters):
        return person("ssi_countable_resources", period.this_year) + person(
            "wi_cts_other_countable_resources", period
        )
