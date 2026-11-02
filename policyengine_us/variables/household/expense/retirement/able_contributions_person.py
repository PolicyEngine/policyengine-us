from policyengine_us.model_api import *


class able_contributions_person(Variable):
    value_type = float
    entity = Person
    label = "Person-level ABLE contributions"
    documentation = (
        "Contributions each person made to an ABLE account. The saver's "
        "credit (26 U.S.C. 25B(d)(1)) allows only contributions to the "
        "person's own account as designated beneficiary, but PE-US has no "
        "separate input for those, so its saver's credit counts this whole "
        "amount. Arizona and Colorado subtract ABLE contributions through "
        "able_contributions."
    )
    reference = "https://www.law.cornell.edu/uscode/text/26/25B#d_1"
    unit = USD
    definition_period = YEAR
