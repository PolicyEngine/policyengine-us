from policyengine_us.model_api import *


class is_ssi_ineligible_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI-ineligible spouse"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1382c#b"

    def formula(person, period, parameters):
        # Check if person is a spouse (either tax unit spouse or head)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        # Check SSI eligibility status
        eligible = person("is_ssi_aged_blind_disabled", period)
        eligible_spouse = person("is_ssi_eligible_spouse", period)

        # A person is an ineligible spouse if they:
        # 1. Are a spouse (either tax unit spouse or head)
        # 2. Are not SSI eligible themselves
        # 3. Are not an SSI eligible spouse
        return is_head_or_spouse & ~eligible_spouse & ~eligible
