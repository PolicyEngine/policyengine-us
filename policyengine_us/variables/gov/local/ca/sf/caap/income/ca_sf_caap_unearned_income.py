from policyengine_us.model_api import *


class ca_sf_caap_unearned_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "San Francisco County CAAP unearned income per person"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    adds = "gov.local.ca.sf.caap.countable_income.sources.unearned"
