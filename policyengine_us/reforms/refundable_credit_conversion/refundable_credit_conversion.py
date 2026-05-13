from policyengine_us.model_api import *


def create_refundable_credit_conversion() -> Reform:
    """Refundable credit conversion reform.

    Adds a flat refundable credit composed of independently toggleable
    components to the federal refundable credit list:

      * per-taxpayer (each head of tax unit and spouse if MFJ)
      * per-CTC-qualifying dependent
      * per-other-dependent (EITC-qualifying child who does NOT meet
        the CTC definition — e.g., children aged 17-18 or full-time
        students 19-23)
      * per-tax-unit (household)
      * per-wage-earner wage subsidy (rate times capped earnings)

    Each component has a boolean switch that gates whether it fires
    (e.g., `use_taxpayer_credit`); when false, that component
    contributes zero regardless of its amount.

    The credit is then summed into federal income tax through the
    standard refundable credit pipeline.

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
            "Flat refundable credit composed of per-taxpayer, per-CTC-"
            "qualifying-dependent, per-other-dependent, per-household, "
            "and per-wage-earner components."
        )

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.refundable_credit_conversion

            person = tax_unit.members

            # Per-taxpayer credit (each head of tax unit and spouse if MFJ).
            if p.credit.use_taxpayer_credit:
                is_filer = person("is_tax_unit_head_or_spouse", period)
                taxpayer_count = tax_unit.sum(is_filer)
                taxpayer_amount = taxpayer_count * p.credit.per_taxpayer
            else:
                taxpayer_amount = 0

            # Per-CTC-qualifying dependent credit — uses the existing
            # ctc_qualifying_children variable so the same eligibility
            # rules as the baseline CTC apply (under 17, dependent, SSN,
            # etc., per IRC §24(c)).
            if p.credit.use_ctc_dependent_credit:
                ctc_count = tax_unit("ctc_qualifying_children", period)
                ctc_dependent_amount = ctc_count * p.credit.per_ctc_dependent
            else:
                ctc_dependent_amount = 0

            # Per-other-dependent credit — EITC-qualifying children who
            # are not CTC-qualifying (e.g., children aged 17-18, full-
            # time students 19-23). Computed as the count difference
            # since CTC-qualifying ⊆ EITC-qualifying in the typical case;
            # max_ guards the rare configuration where a CTC kid lacks
            # the EITC identification requirements.
            if p.credit.use_other_dependent_credit:
                eitc_count = tax_unit("eitc_child_count", period)
                ctc_count_inner = tax_unit("ctc_qualifying_children", period)
                other_count = max_(eitc_count - ctc_count_inner, 0)
                other_dependent_amount = other_count * p.credit.per_other_dependent
            else:
                other_dependent_amount = 0

            # Per-tax-unit (household) credit.
            household_amount = (
                p.credit.per_household if p.credit.use_household_credit else 0
            )

            # Per-wage-earner wage subsidy.
            if p.wage_credit.use_wage_credit:
                earnings = person("earned_income", period)
                capped_earnings = min_(max_(earnings, 0), p.wage_credit.cap)
                person_wage_credit = capped_earnings * p.wage_credit.rate
                wage_credit_amount = tax_unit.sum(person_wage_credit)
            else:
                wage_credit_amount = 0

            return (
                taxpayer_amount
                + ctc_dependent_amount
                + other_dependent_amount
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
