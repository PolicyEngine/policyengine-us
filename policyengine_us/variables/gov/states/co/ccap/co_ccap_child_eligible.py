from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ccap.co_ccap_parameter_instant import (
    co_ccap_parameter_instant,
)


class co_ccap_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Child eligibility for Colorado Child Care Assistance Program"
    reference = (
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=17",
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=35",
        "https://spl.cde.state.co.us/artemis/huserials/hu62510internet/hu62510202527internet.pdf#page=23",
    )
    definition_period = MONTH
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        instant_str = co_ccap_parameter_instant(period)
        p = parameters(instant_str).gov.states.co.ccap
        # Section 3.105.1(F) (now 3.111(F)) extends the under-19 limit to
        # children under court supervision; the required documentation of care
        # needs is a verification detail, as is_disabled is for verified
        # incapacity.
        disabled = person("is_disabled", period.this_year)
        court_supervision = person("is_under_court_supervision", period.this_year)
        age_limit = where(
            disabled | court_supervision, p.disabled_age_limit, p.age_limit
        )
        age_eligible = person("age", period.this_year) < age_limit
        return age_eligible & person("is_tax_unit_dependent", period.this_year)
