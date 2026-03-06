from policyengine_us.model_api import *


class ca_cpuc_countable_income(Variable):
    value_type = float
    entity = Household
    label = "CA CPUC countable income for CARE/FERA"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.CA
    adds = "gov.states.ca.cpuc.income_sources"
