from policyengine_us.model_api import *


class il_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ilga.gov/Documents/legislation/103/HB/10300HB4917.htm"
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.credits.ctc
        person = tax_unit.members
        age = person("age", period)
        # 35 ILCS 5/212.3 incorporates IRC §32 EITC qualifying-child rules,
        # which tie to IRC §152(c) (excluding §152(d) qualifying relatives).
        qualifying_child = person("is_qualifying_child_dependent", period)
        eligible_child = qualifying_child & (age < p.age_limit)
        eligible_child_present = tax_unit.any(eligible_child)
        state_eitc = tax_unit("il_eitc", period)
        return eligible_child_present * state_eitc * p.rate
