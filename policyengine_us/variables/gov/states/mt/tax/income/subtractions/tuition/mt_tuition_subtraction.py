from policyengine_us.model_api import *


class mt_tuition_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana tuition subtraction"
    definition_period = YEAR
    reference = "https://leg.mt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html"
    defined_for = StateCode.MT

    adds = ["mt_tuition_subtraction_person"]
