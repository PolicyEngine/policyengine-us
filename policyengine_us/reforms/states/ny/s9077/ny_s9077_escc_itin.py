from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ny_s9077_escc_itin() -> Reform:
    """
    NY Senate Bill S.9077 - Empire State Child Credit ITIN Expansion

    Allows children with ITINs to qualify for the Empire State Child Credit
    starting in tax year 2027. Under current law (2025-2026), only children
    with SSNs qualify (tied to federal CTC requirements).

    Reference: https://www.nysenate.gov/legislation/bills/2025/S9077
    Section D(V): "is a citizen or national of the United States, or an
    individual with an individual taxpayer identification number issued
    by the internal revenue service"
    """

    class ny_ctc_post_2024_base(Variable):
        value_type = float
        entity = TaxUnit
        label = "New York CTC post-2024 base amount"
        documentation = (
            "Base New York CTC amount before phase-out under post-2024 rules. "
            "Under S.9077, children with ITINs qualify starting 2027."
        )
        unit = USD
        definition_period = YEAR
        reference = ("https://www.nysenate.gov/legislation/bills/2025/S9077",)
        defined_for = "ny_ctc_post_2024_eligible"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ny.tax.income.credits.ctc
            person = tax_unit.members
            age = person("age", period)

            # S.9077: Allow ITIN holders (Section D(V))
            # Requires: dependent status + has ITIN/SSN + meets age threshold
            is_dependent = person("is_tax_unit_dependent", period)
            has_valid_id = person("has_itin", period)
            age_thresholds = p.post_2024.amount.thresholds
            max_age = age_thresholds[-1]
            age_eligible = age < max_age
            qualifies = is_dependent & has_valid_id & age_eligible

            # Apply minimum age requirement
            qualifies = qualifies & (age >= p.minimum_age)

            # Calculate credit amount by age using scale parameter
            credit_by_age = p.post_2024.amount.calc(age)
            qualifying_credit = qualifies * credit_by_age

            return tax_unit.sum(qualifying_credit)

    class ny_ctc_post_2024_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "New York CTC post-2024 eligibility"
        documentation = (
            "Whether the tax unit is eligible for New York CTC under "
            "post-2024 rules. Under S.9077, ITIN children qualify from 2027."
        )
        definition_period = YEAR
        reference = "https://www.nysenate.gov/legislation/bills/2025/S9077"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ny.tax.income.credits.ctc

            # Only eligible if post-2024 rules are in effect
            if not p.post_2024.in_effect:
                return False

            person = tax_unit.members
            age = person("age", period)

            # S.9077: Allow ITIN holders
            is_dependent = person("is_tax_unit_dependent", period)
            has_valid_id = person("has_itin", period)
            age_thresholds = p.post_2024.amount.thresholds
            max_age = age_thresholds[-1]
            age_eligible = age < max_age
            qualifies = is_dependent & has_valid_id & age_eligible

            # Apply minimum age requirement
            qualifies = qualifies & (age >= p.minimum_age)

            # Check if any children get a non-zero credit amount
            credit_by_age = p.post_2024.amount.calc(age)
            qualifying_children = qualifies & (credit_by_age > 0)

            total_qualifying_children = tax_unit.sum(qualifying_children)
            return total_qualifying_children > 0

    class reform(Reform):
        def apply(self):
            self.update_variable(ny_ctc_post_2024_base)
            self.update_variable(ny_ctc_post_2024_eligible)

    return reform


def create_ny_s9077_escc_itin_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ny_s9077_escc_itin()

    p = parameters.gov.contrib.states.ny.s9077

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ny_s9077_escc_itin()
    else:
        return None


ny_s9077_escc_itin = create_ny_s9077_escc_itin_reform(None, None, bypass=True)
