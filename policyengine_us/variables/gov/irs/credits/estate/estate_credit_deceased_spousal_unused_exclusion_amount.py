from policyengine_us.model_api import *


class estate_credit_deceased_spousal_unused_exclusion_amount(Variable):
    value_type = float
    entity = Person
    label = "Estate credit deceased spousal unused amount"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/2010"

    def formula(person, period, parameters):
        unused_amount = person("estate_credit_basic_exclusion_amount", period)
        deceased_spouse = person.tax_unit("spouse_is_deceased", period)

        return unused_amount * deceased_spouse
