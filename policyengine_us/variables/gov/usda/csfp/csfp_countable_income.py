from policyengine_us.model_api import *


class csfp_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Income used for CSFP direct eligibility"
    documentation = (
        "SPM unit income for CSFP direct eligibility. The model retains its "
        "existing approximation pending a separate review of program exclusions."
    )
    reference = "https://www.govinfo.gov/content/pkg/CFR-2026-title7-vol4/pdf/CFR-2026-title7-vol4-sec247-9.pdf#page=2"

    adds = "gov.usda.csfp.income.sources"
