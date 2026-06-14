from policyengine_us.model_api import *


class ca_sf_caap_food_provided_in_kind(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Food provided in-kind for San Francisco County CAAP"
    definition_period = MONTH
    defined_for = "in_san_francisco"
    # Defaults to no in-kind food provided, so the in-kind value is zero
    # unless this flag is set (SEC. 20.7-22 / Div 99-1).
    default_value = False
