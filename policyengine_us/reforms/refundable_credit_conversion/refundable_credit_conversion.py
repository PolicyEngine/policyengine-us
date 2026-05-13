from policyengine_us.model_api import *


def create_refundable_credit_conversion() -> Reform:
    """Refundable credit conversion reform.

    Adds a flat refundable credit composed of per-taxpayer, per-dependent,
    per-household, and per-worker wage-credit components to the federal
    refundable credit list. The credit is then summed into the federal
    income tax through the standard refundable credit pipeline.

    Eliminations of baseline credits and deductions (CTC, EITC, standard
    deduction, itemized deductions, above-the-line deductions, Head of
    Household filing) are handled by direct overrides to the existing
    baseline parameters — this contrib reform only ships the new credit.
    """

    class flat_refundable_credit(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Refundable credit conversion flat credit"
        unit = USD
        documentation = (
            "Flat refundable credit composed of per-taxpayer, per-dependent, "
            "per-household, and per-worker wage-credit components."
        )

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.refundable_credit_conversion

            person = tax_unit.members
            is_filer = person("is_tax_unit_head_or_spouse", period)
            taxpayer_count = tax_unit.sum(is_filer)

            # 0 = EITC-qualifying children (default), 1 = CTC-qualifying
            # children, 2 = all claimed tax-unit dependents.
            definition = int(p.credit.dependent_definition)
            if definition == 1:
                dependent_count = tax_unit("ctc_qualifying_children", period)
            elif definition == 2:
                dependent_count = tax_unit("tax_unit_count_dependents", period)
            else:
                dependent_count = tax_unit("eitc_child_count", period)

            taxpayer_amount = taxpayer_count * p.credit.per_taxpayer
            dependent_amount = dependent_count * p.credit.per_dependent
            household_amount = p.credit.per_household

            earnings = person("earned_income", period)
            capped_earnings = min_(max_(earnings, 0), p.wage_credit.cap)
            person_wage_credit = capped_earnings * p.wage_credit.rate
            wage_credit_amount = tax_unit.sum(person_wage_credit)

            return (
                taxpayer_amount
                + dependent_amount
                + household_amount
                + wage_credit_amount
            )

    class income_tax_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "federal refundable income tax credits"
        unit = USD

        def formula(tax_unit, period, parameters):
            base = list(parameters(period).gov.irs.credits.refundable)
            credits = base + ["flat_refundable_credit"]
            return add(tax_unit, period, credits)

    class reform(Reform):
        def apply(self):
            self.update_variable(flat_refundable_credit)
            self.update_variable(income_tax_refundable_credits)

    return reform


def create_refundable_credit_conversion_reform(
    parameters, period, bypass: bool = False
):
    """Auto-application function for the refundable credit conversion reform."""
    if bypass:
        return create_refundable_credit_conversion()

    from policyengine_core.periods import period as period_

    p = parameters.gov.contrib.refundable_credit_conversion

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_refundable_credit_conversion()
    else:
        return None


refundable_credit_conversion = create_refundable_credit_conversion()
