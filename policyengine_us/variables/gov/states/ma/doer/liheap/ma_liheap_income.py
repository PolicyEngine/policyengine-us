from policyengine_us.model_api import *


class ma_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts LIHEAP income"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/info-details/learn-about-home-energy-assistance-heap"

    # The income concept is not clearly defined, assuming IRS gross income
    adds = ["irs_gross_income"]
