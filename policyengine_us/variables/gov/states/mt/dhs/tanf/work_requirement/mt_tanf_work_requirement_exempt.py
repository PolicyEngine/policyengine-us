from policyengine_us.model_api import *


class mt_tanf_work_requirement_exempt(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Exempt from working requirement for Montana Temporary Assistance for Needy Families (TANF)"
    reference = "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.103"  # (62)
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        # (1) Eligible children who are not the head of an assistance unit can be exempt
        # do I need to model this rule:
        # a minor parent who is not the head of a household or the spouse of the head of the household;
        eligible_child = person("mt_tanf_eligible_child", period) & ~person(
            "is_tax_unit_head", period
        )

        # (2) Members receiving SSI are exempt
        receives_ssi = person("ssi", period) > 0

        # (3) Ineligible aliens (non-citizens who are not eligible for TANF) are exempt

        return eligible_child | receives_ssi
