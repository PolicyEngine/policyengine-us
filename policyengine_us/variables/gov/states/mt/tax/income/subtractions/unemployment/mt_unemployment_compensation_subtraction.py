from policyengine_us.model_api import *


class mt_unemployment_compensation_subtraction(Variable):
    value_type = float
    entity = Person
    label = "Montana unemployment compensation subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        # 2021 Form 2 instructions, Montana Subtractions Schedule, line 7:
        # unemployment benefits from Montana or another state are exempt;
        # enter the amount reported on federal Schedule 1, line 7.
        "https://taxsim.nber.org/historical_state_tax_forms/MT/2021/form%202%202021%20instructions.pdf#page=25",
        # Former 15-30-2110, MCA; repealed by SB 399 (Ch. 503, L. 2021)
        # effective tax year 2024, after which unemployment compensation
        # is taxable in Montana.
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0100/0150-0300-0210-0100.html",
    )
    defined_for = StateCode.MT

    adds = ["taxable_unemployment_compensation"]
