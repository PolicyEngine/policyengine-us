from policyengine_us.model_api import *


class ca_oc_general_relief_gross_unearned_income(Variable):
    value_type = float
    entity = Person
    label = "Orange County General Relief gross unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = "in_oc"
    adds = "gov.local.ca.oc.general_relief.income.sources.unearned"
