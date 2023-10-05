from policyengine_us.model_api import *


class co_ccap_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Child eligibility for Colorado Child Care Assistance Program"
    reference = (
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=6",
        "https://docs.google.com/spreadsheets/d/1WzobLnLoxGbN_JfTuw3jUCZV5N7IA_0uvwEkIoMt3Wk/edit#gid=1350122430",
    )
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        tax_unit = person.tax_unit
        co_swap_year = tax_unit("co_swap_year", period)[0]
        p = parameters(co_swap_year).gov.states.co.ccap
        # child < 13 or disabled child < 19 to be eligible
        disabled = person("is_disabled", period)
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        return where(
            disabled,
            (age < p.disabled_child_age_limit) & dependent,
            (age < p.age_limit) & dependent,
        )
