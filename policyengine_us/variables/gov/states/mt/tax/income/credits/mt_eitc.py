from policyengine_us.model_api import *


class mt_eitc(Variable):
    value_type = float
    entity = Person
    label = "Montana EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0180/0150-0300-0230-0180.html"

    def formula(person, period, parameters):
        federal_eitc = person.tax_unit("eitc", period)
        filing_status = person.tax_unit("filing_status", period)
        rate = parameters(period).gov.states.mt.tax.income.credits.eitc.rate
        # Since the eitc amount can be attributed to either spouse, we will allocate the 
        # value to the head
        is_head = person("is_tax_unit_head", period)
        return is_head * where(
            filing_status == filing_status.possible_values.SEPARATE,
            0,
            federal_eitc * rate,
        )
