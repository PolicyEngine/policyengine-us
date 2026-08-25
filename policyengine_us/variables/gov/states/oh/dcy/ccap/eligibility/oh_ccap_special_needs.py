from policyengine_us.model_api import *


class oh_ccap_special_needs(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Whether the child has verified Ohio CCAP special needs"
    defined_for = StateCode.OH
    reference = "https://codes.ohio.gov/ohio-administrative-code/rule-5180:2-16-01"

    def formula(person, period, parameters):
        # 5180:2-16-01(AA): a special needs child has a chronic health
        # condition or is not meeting developmental expectations; is_disabled
        # proxies the chronic-health-condition prong. Consumers apply the
        # under-18 age bound from (AA).
        return person("is_disabled", period.this_year) | person(
            "has_developmental_delay", period.this_year
        )
