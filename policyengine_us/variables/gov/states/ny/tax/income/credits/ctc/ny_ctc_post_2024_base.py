from policyengine_us.model_api import *


class ny_ctc_post_2024_base(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York CTC post-2024 base amount"
    documentation = (
        "Base New York CTC amount before phase-out under post-2024 rules"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c-1)
    defined_for = "ny_ctc_post_2024_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc
        person = tax_unit.members
        age = person("age", period)

        # Post-2024 CTC rules (2025-2027)
        qualifies_for_federal_ctc = person("ctc_qualifying_child", period)
        qualifies = qualifies_for_federal_ctc & (age >= p.minimum_age)

        # Calculate credit amount by age using scale parameter
        credit_by_age = p.post_2024.amount.calc(age)
        qualifying_credit = qualifies * credit_by_age

        return tax_unit.sum(qualifying_credit)
