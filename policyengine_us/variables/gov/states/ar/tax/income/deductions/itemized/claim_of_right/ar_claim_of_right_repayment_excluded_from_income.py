from policyengine_us.model_api import *


class ar_claim_of_right_repayment_excluded_from_income(Variable):
    value_type = float
    entity = Person
    label = "Claim of right repayment not included in Arkansas income when received"
    unit = USD
    documentation = (
        "Part of claim_of_right_repayment that was not included in Arkansas "
        "gross income in the earlier year it was received, such as income "
        "received while a nonresident that Arkansas did not tax. Arkansas's "
        "claim of right deduction excludes it."
    )
    definition_period = YEAR
    reference = (
        # Ark. Code § 26-51-457(a), adopting 26 U.S.C. § 1341(a)(1)
        "https://www.arkleg.state.ar.us/Acts/FTPDocument?path=%2FACTS%2F2013R%2FPublic%2F&file=1284.pdf&ddBienniumSession=2013%2F2013R#page=1",
    )
    defined_for = StateCode.AR
