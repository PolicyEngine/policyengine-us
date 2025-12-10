from policyengine_us.model_api import *


class il_smib_person(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Illinois SMIB benefit (person)"
    definition_period = MONTH
    documentation = (
        "Illinois Supplementary Medical Insurance Benefit (SMIB) Buy-In "
        "Program benefit. The state pays the Medicare Part B premium for "
        "eligible individuals."
    )
    reference = (
        "https://www.ilga.gov/commission/jcar/admincode/089/089001200D00700R.html",
        "https://www.dhs.state.il.us/page.aspx?item=18685",
    )
    defined_for = "il_smib_eligible"

    def formula(person, period, parameters):
        # SMIB pays the Part B premium
        # base_part_b_premium is annual, convert to monthly
        return person("base_part_b_premium", period.this_year) / MONTHS_IN_YEAR
