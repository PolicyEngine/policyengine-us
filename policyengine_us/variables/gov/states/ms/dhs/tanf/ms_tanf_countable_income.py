from policyengine_us.model_api import *


class ms_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Mississippi TANF countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = (
        "https://www.mdhs.ms.gov/wp-content/uploads/2018/02/MDHS_TANF-Eligibility-Flyer.pdf",
        "https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19",
    )
    # NOTE: Mississippi has 6-month and 3-month total earned income disregards
    # that cannot be tracked in PolicyEngine. This simplified implementation
    # uses gross income without those time-limited disregards.

    adds = ["tanf_gross_earned_income", "tanf_gross_unearned_income"]
