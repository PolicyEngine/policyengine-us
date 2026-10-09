from policyengine_us.model_api import *


class tax_unit_claim_of_right_repayment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Repayment of claim of right income on the return"
    unit = USD
    documentation = (
        "Total repaid this year by the head and spouse of income included in "
        "an earlier year under a claim of right, excluding repayments "
        "deducted in arriving at adjusted gross income. Dependents' "
        "repayments belong on their own returns."
    )
    definition_period = YEAR
    reference = (
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title26/html/USCODE-2024-title26-subtitleA-chap1-subchapQ-partV-sec1341.htm",
        # Publication 525 (2025), Repayments: consider the total amount
        # repaid on the return
        "https://www.irs.gov/pub/irs-prior/p525--2025.pdf#page=36",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        repayment = person("claim_of_right_repayment", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.sum(repayment * head_or_spouse)
