from policyengine_us.model_api import *


class ca_is_qualifying_child_for_caleitc(Variable):
    value_type = bool
    entity = Person
    label = "Child qualifies for CalEITC"
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/file/personal/credits/california-earned-income-tax-credit.html#What-you-ll-get"
