from policyengine_us.model_api import *


class al_retirement_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama retirement exemption"
    unit = USD
    # Alabama Schedule RS Part II & III Line 10, Alabama Form 40 Booklet Page 14 Pension & Annuities, Alabama Legal Section 40-18-19 (a)(13)
    reference = (
        "https://www.revenue.alabama.gov/wp-content/uploads/2024/01/23schrsinstr.pdf#page=1",
        "https://www.revenue.alabama.gov/ultraviewer/viewer/basic_viewer/index.html?form=2024/01/23f40bk.pdf#page=14",
        "https://alison.legislature.state.al.us/code-of-alabama?section=40-18-19",
    )
    definition_period = YEAR
    defined_for = StateCode.AL

    adds = ["al_retirement_exemption_person"]
