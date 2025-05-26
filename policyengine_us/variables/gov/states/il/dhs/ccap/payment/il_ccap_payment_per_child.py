from policyengine_us.model_api import *


class il_ccap_payment_per_child(Variable):
    value_type = float
    entity = Person
    label = "Illinois Child Care Assistance Program (CCAP) payment per child"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-50.320"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap
        county_group = person.spm_unit("il_ccap_county_group", period)
        day_care_category = person("il_ccap_day_care_category", period)
        age_category = person("il_ccap_age_category", period)
        payment_rate_per_day = p.payment[county_group][day_care_category][
            age_category
        ]
        # We assume the child goes to day care center 20 days a month.
        return payment_rate_per_day * p.day_care_attending_days
