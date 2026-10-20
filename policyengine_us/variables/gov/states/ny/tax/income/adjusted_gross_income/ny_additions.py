from policyengine_us.model_api import *


class ny_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York AGI additions"
    unit = USD
    documentation = "Additions to NY AGI over federal AGI."
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/20-NYCRR-112.2",
        # 2020 Form IT-558 instructions, addition A-003: the IRC 62(a)(22)
        # charitable deduction, which recomputes federal AGI (IT-201 line
        # 19a).
        "https://www.tax.ny.gov/pdf/2020/inc/it558i_2020.pdf#page=2",
    )
    defined_for = StateCode.NY

    adds = ["ny_other_additions", "charitable_contributions_ald"]
