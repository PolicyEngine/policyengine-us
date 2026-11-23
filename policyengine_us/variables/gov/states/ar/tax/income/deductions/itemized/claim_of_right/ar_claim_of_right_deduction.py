from policyengine_us.model_api import *


class ar_claim_of_right_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas claim of right deduction"
    unit = USD
    documentation = (
        "Arkansas itemized deduction for restoring more than $3,000 of income "
        "included in Arkansas gross income in an earlier year under a claim "
        "of right (Ark. Code § 26-51-457, from 2013). Arkansas adopts 26 "
        "U.S.C. § 1341(a)(1)-(3) but not the federal choice of a credit, so "
        "the deduction applies whichever federal method governs. Ark. Code "
        "§ 26-51-437(b) does not list it among the itemized deductions that "
        "are not miscellaneous, so the model counts it toward the 2% floor. "
        "Not modeled: repayments of $3,000 or less, which § 26-51-457 does "
        "not reach; whether another provision allows them is unresolved."
    )
    definition_period = YEAR
    reference = (
        # Ark. Code § 26-51-457, enacted by Act 1284 of 2013; PDF pages 1-2
        "https://www.arkleg.state.ar.us/Acts/FTPDocument?path=%2FACTS%2F2013R%2FPublic%2F&file=1284.pdf&ddBienniumSession=2013%2F2013R#page=1",
        # Ark. Code § 26-51-437, enacted by Act 382 of 1987, § 28
        "https://www.arkleg.state.ar.us/Acts/FTPDocument?path=%2FACTS%2F1987R%2FPublic%2F&file=382.pdf&ddBienniumSession=1987%2F1987R#page=9",
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ar.tax.income.deductions.itemized.claim_of_right
        person = tax_unit.members
        repayment = person("claim_of_right_repayment", period)
        excluded = person("ar_claim_of_right_repayment_excluded_from_income", period)
        # Dependents' repayments belong on their own returns.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        restored = tax_unit.sum(max_(repayment - excluded, 0) * head_or_spouse)
        # Section 1341(a)(3), as adopted: the total restored on the return
        # must exceed the threshold.
        return where(restored > p.threshold, restored, 0)
