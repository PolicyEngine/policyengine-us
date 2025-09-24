from policyengine_us.model_api import *


class dc_income_subtractions(Variable):
    value_type = float
    entity = Person
    label = "DC subtractions from federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=63"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=55"
    )
    defined_for = StateCode.DC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.tax.income.subtractions
        total_subtractions = add(person, period, p.sources)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
