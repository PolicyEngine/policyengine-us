from policyengine_us.model_api import *


class mt_tanf_work_requirement_exempt(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Exempt from working requirement for Montana Temporary Assistance for Needy Families (TANF)"
    reference = "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.103"  # (62)
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        # look for more rules about work requirement exemption
        eligible_child = person("mt_tanf_eligible_child", period)


        return eligible_child
