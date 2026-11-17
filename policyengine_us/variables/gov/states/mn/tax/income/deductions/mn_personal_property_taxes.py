from policyengine_us.model_api import *


class mn_personal_property_taxes(Variable):
    value_type = float
    entity = Person
    label = "Personal property taxes paid for Minnesota itemized deductions"
    unit = USD
    definition_period = YEAR
    default_value = 0
    documentation = "State and local personal property taxes paid during the year, excluding real estate taxes, for Minnesota Schedule M1SA."
    reference = "https://www.revisor.mn.gov/statutes/cite/290.0122#stat.290.0122.3"
    defined_for = StateCode.MN
