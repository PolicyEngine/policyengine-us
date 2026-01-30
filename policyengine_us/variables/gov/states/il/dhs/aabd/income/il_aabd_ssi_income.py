from policyengine_us.model_api import *


class il_aabd_ssi_income(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    unit = USD
    label = "SSI income for IL AABD calculation"
    documentation = (
        "SSI amount used in IL AABD unearned income calculation. "
        "By default, uses calculated ssi. When il_aabd_use_reported_ssi "
        "is True, uses ssi_reported instead."
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        use_reported = person("il_aabd_use_reported_ssi", period.this_year)
        reported = person("ssi_reported", period)
        calculated = person("ssi", period)
        return where(use_reported, reported, calculated)
