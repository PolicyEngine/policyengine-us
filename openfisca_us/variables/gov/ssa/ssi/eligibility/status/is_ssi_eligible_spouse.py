from openfisca_us.model_api import *


class is_ssi_eligible_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-eligible spouse"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382c#b"

    def formula(person, period, parameters):
        both_aged_blind_disabled = (
            add(person.marital_unit, period, ["is_ssi_aged_blind_disabled"])
            == 2
        )
        spouse = person("is_tax_unit_spouse", period)
        return spouse & both_aged_blind_disabled
