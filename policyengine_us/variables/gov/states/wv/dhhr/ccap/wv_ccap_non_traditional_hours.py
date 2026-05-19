from policyengine_us.model_api import *


class wv_ccap_non_traditional_hours(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Whether child receives care during non-traditional hours for West Virginia CCAP"
    defined_for = StateCode.WV
    reference = "https://bfa.wv.gov/media/6831/download?inline#page=1"
