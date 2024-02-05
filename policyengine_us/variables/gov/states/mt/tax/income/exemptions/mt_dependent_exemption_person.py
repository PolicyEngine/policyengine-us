from policyengine_us.model_api import *


class mt_dependent_exemption_person(Variable):
    value_type = float
    entity = Person
    label = "Montana dependent exemption for each person"
    unit = USD
    definition_period = YEAR
    reference = "https://regulations.justia.com/states/montana/department-42/chapter-42-15/subchapter-42-15-4/rule-42-15-403/"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        # Qualifying child under IRC 152(c), which defines for the EITC
        qualifying_child = person("is_eitc_qualifying_child", period)
        # Disabled dependents get an additional exemption.
        disabled = where(
            qualifying_child, person("is_disabled", period).astype(int), 0
        )
        # Allocate the dependent exemptions to the head
        return qualifying_child + disabled
