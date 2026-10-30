from policyengine_us.model_api import *


class ia_ssa_countable_for_hud(Variable):
    value_type = float
    entity = Person
    label = "Iowa State Supplementary Assistance countable for HUD"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    # 24 CFR 5.609(b)(6) and (b)(19)
    reference = "https://www.ecfr.gov/current/title-24/section-5.609#p-5.609(b)(6)"

    def formula(person, period, parameters):
        # 24 CFR 5.609(b)(6) excludes amounts "specifically for, or in
        # reimbursement of, the cost of health and medical care expenses", and
        # (b)(19) excludes state agency payments "to enable a family member who
        # has a disability to reside in the family's assisted unit". Both cover
        # the in-home health-related care payment; the blind supplement paid
        # alongside it remains income.
        category = person("ia_ssa_category", period)
        home_care = category == category.possible_values.IN_HOME_CARE
        return where(
            home_care, person("ia_ssa_federal", period), person("ia_ssa", period)
        )
