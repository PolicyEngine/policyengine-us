from policyengine_us.model_api import *


class me_military_retirement_pay_subtractions(Variable):
    value_type = float
    entity = Person
    label = "ME military retirement pay subtractions"
    unit = USD
    definition_period = YEAR
    documentation = "The benefits received under a United States military retirement plan, including survivor benefits, are fully exempt from Maine income tax. See 2022 - Worksheet for Pension Income Deduction below."
    reference = "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/22_1040me_sched_1s_ff.pdf"
