from policyengine_us.model_api import *


class is_paid_hourly(Variable):
    value_type = bool
    entity = Person
    label = "is paid hourly"
    reference = "https://www.federalregister.gov/documents/2024/04/26/2024-08038/defining-and-delimiting-the-exemptions-for-executive-administrative-professional-outside-sales-and"
    definition_period = YEAR
