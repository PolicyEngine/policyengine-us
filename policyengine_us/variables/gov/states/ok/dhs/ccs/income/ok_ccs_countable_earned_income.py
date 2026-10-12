from policyengine_us.model_api import *


class ok_ccs_countable_earned_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Oklahoma Child Care Subsidy countable earned income"
    definition_period = MONTH
    defined_for = StateCode.OK
    reference = "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-40-7-11"

    def formula(person, period, parameters):
        return (
            person("employment_income", period)
            + max_(person("self_employment_income", period), 0)
            + max_(person("sstb_self_employment_income", period), 0)
            + max_(person("farm_operations_income", period), 0)
            + max_(person("rental_income", period), 0)
        )
