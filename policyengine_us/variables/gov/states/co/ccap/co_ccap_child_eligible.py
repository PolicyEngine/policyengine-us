from policyengine_us.model_api import *


class co_ccap_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Child eligibility for Colorado Child Care Assistance Program"
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=6"
    definition_period = MONTH
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        year = period.start.year
        if period.start.month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        p = parameters(instant_str).gov.states.co.ccap
        # child < 13 or disabled child < 19 to be eligible
        disabled = person("is_disabled", period.this_year)
        age_limit = where(disabled, p.disabled_age_limit, p.age_limit)
        age_eligible = person("age", period.this_year) < age_limit
        return age_eligible & person("is_tax_unit_dependent", period.this_year)
