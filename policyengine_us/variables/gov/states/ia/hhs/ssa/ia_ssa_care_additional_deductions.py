from policyengine_us.model_api import *


class ia_ssa_care_additional_deductions(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA approved additional care income deductions"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.IA
    documentation = "Verified monthly deductions from care income beyond those the model applies: dependent and spouse allocations and unmet medical needs, and for residential care also approved first-month expenses of the previous living arrangement and work-related deductions. Excludes the home maintenance or personal needs allowance and the $65 and one-half earnings exclusions. Key each amount to its month; a yearly entry is spread evenly over the months."
    reference = (
        # 441 IAC 52.1(3)"a"
        "https://www.legis.iowa.gov/docs/iac/chapter/441.52.pdf#page=1",
        # PDF pages 42-43, 61-64
        "https://hhs.iowa.gov/media/3987/download?inline=#page=42",
    )

    def formula(person, period, parameters):
        # A formula stops a one-month input from carrying into later months.
        return 0
