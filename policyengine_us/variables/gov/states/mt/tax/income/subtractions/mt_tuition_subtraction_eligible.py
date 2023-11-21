from policyengine_us.model_api import *


class mt_tuition_subtraction_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Montana tuition subtraction"
    definition_period = YEAR
    reference = "https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        contributions = add(tax_unit, period, ["investment_in_529_plan"])
        return contributions > 0
