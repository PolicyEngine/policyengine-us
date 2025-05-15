from policyengine_us.model_api import *


class is_eligible_for_fsla_overtime_protection(Variable):
    value_type = bool
    entity = Person
    label = "Is eligible for overtime pay"
    reference = "https://www.federalregister.gov/documents/2024/04/26/2024-08038/defining-and-delimiting-the-exemptions-for-executive-administrative-professional-outside-sales-and"
    definition_period = YEAR

    def formula(person, period, parameters):
        return True
