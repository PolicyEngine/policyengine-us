from policyengine_us.model_api import *


class or_ssp_countable_for_hud(Variable):
    value_type = float
    entity = Person
    label = "Oregon SSP countable for HUD"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.OR
    reference = (
        # 24 CFR 5.609(b)(19)
        "https://www.law.cornell.edu/cfr/text/24/5.609",
        # DHS 2818 (10/2026)
        "https://sharedsystems.dhsoha.state.or.us/DHSForms/Served/de2818.pdf#page=583",
    )
    documentation = "The Oregon SSP payment without the in-home supplement, which reimburses uncovered assistance needs of a person receiving in-home services."

    def formula(person, period, parameters):
        category = person("or_ssp_category", period)
        in_home = category == category.possible_values.IN_HOME
        return where(in_home, 0, person("or_ssp", period))
