from policyengine_us.model_api import *


class mt_eitc(Variable):
    value_type = float
    entity = Person
    label = "Montana EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0180/0150-0300-0230-0180.html"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        federal_eitc = person.tax_unit("eitc", period)
        p = parameters(period).gov.states.mt.tax.income.credits.eitc
        # Since the eitc amount can be attributed to either spouse, we will allocate the
        # value to the head
        is_head = person("is_tax_unit_head", period)
        state_eitc = federal_eitc * p.match
        # Separate filers are inleigible for the Montana EITC, this case is currently
        # excluded as we only model separate filing on the same return
        return is_head * state_eitc
