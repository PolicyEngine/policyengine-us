from policyengine_us.model_api import *


class il_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Illinois Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ilga.gov/legislation/fulltext.asp?DocName=&SessionId=112&GA=103&DocTypeId=HB&DocNum=4917&GAID=17&LegID=152789&SpecSess=&Session="
    defined_for = StateCode.IL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.il.tax.income.credits.ctc
        person = tax_unit.members
        age = person("age", period)
        age_eligible_child = age < p.age_limit
        federal_ctc_eligible_child = person("ctc_qualifying_child", period)
        eligible_child = age_eligible_child & federal_ctc_eligible_child
        eligible_child_present = tax_unit.any(eligible_child)
        state_eitc = tax_unit("il_eitc", period)
        return eligible_child_present * state_eitc * p.rate
