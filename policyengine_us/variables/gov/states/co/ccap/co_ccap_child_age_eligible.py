from policyengine_us.model_api import *


class co_ccap_child_age_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Colorado Child Care Assistance Program child age eligible"
    unit = USD
    reference = (
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=6",
        "https://docs.google.com/spreadsheets/d/1WzobLnLoxGbN_JfTuw3jUCZV5N7IA_0uvwEkIoMt3Wk/edit#gid=1350122430",
    )
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.ccap
        # child < 13 or disabled child < 19 to be eligible
        disabled = person("is_disabled", period)
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        return where(
            disabled,
            (age < p.disabled_child_age_limit) & dependent,
            (age < p.age_limit) & dependent,
        )
