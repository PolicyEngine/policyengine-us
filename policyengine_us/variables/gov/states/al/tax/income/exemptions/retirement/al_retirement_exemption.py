from policyengine_us.model_api import *


class al_retirement_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama retirement exemption"
    unit = USD
    # The Code of Alabama Section 40-18-19 (a)(13).
    documentation = "https://casetext.com/statute/code-of-alabama/title-40-revenue-and-taxation/chapter-18-income-taxes/article-1-general-provisions/section-40-18-19-exemptions-generally"
    definition_period = YEAR
    defined_for = StateCode.AL

    adds = ["al_retirement_exemption_eligible_person"]
