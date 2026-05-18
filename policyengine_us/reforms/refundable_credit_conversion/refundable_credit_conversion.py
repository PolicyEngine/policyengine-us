from policyengine_us.model_api import *
from policyengine_core.periods import instant
from policyengine_core.periods import period as period_


def create_refundable_credit_conversion() -> Reform:
    """Refundable credit conversion reform.

    Adds a flat refundable credit composed of independently toggleable
    components to the federal refundable credit list (`gov.irs.credits.refundable`):

      * per-taxpayer (each head of tax unit and spouse if MFJ)
      * per-CTC-qualifying dependent
      * per-other-dependent (EITC-qualifying child who does NOT meet
        the CTC definition — e.g., children aged 17-18 or full-time
        students 19-23)
      * per-tax-unit (household)
      * per-earner earnings subsidy (rate times capped earnings per
        worker, where earnings follow the EITC convention of wages
        plus self-employment income)

    Each component has a boolean switch that gates whether it fires
    (e.g., `use_taxpayer_credit`); when false, that component
    contributes zero regardless of its amount.

    The reform appends `flat_refundable_credit` to the
    `gov.irs.credits.refundable` parameter (a list of variable names
    summed into the federal refundable-credits total). Existing list
    contents are preserved at every historical transition. The base
    `income_tax_refundable_credits` variable is unmodified; it picks up
    the appended credit through its existing `adds` attribute.

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
        reference = "https://github.com/PolicyEngine/policyengine-us/pull/8219"

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

            # Per-CTC-qualifying dependent credit (reuses the baseline
            # `ctc_qualifying_children` variable; same eligibility rules
            # as the federal CTC per IRC §24(c)). Hoisted so the
            # per-other-dependent branch can reuse the same count.
            ctc_count = tax_unit("ctc_qualifying_children", period)
            if p.credit.use_ctc_dependent_credit:
                ctc_dependent_amount = ctc_count * p.credit.per_ctc_dependent
            else:
                ctc_dependent_amount = 0

            # Per-other-dependent credit (EITC-qualifying children who
            # are not CTC-qualifying — e.g., children aged 17-18 or
            # full-time students aged 19-23). Computed as a population-
            # aggregate count difference; the max_ guard handles the
            # rare case where a CTC kid lacks the EITC identification
            # requirements (ctc_count > eitc_count).
            if p.credit.use_other_dependent_credit:
                eitc_count = tax_unit("eitc_child_count", period)
                other_count = max_(eitc_count - ctc_count, 0)
                other_dependent_amount = other_count * p.credit.per_other_dependent
            else:
                other_dependent_amount = 0

            household_amount = (
                p.credit.per_household if p.credit.use_household_credit else 0
            )

            # Per-earner earnings subsidy (rate * capped earnings per
            # worker, summed across the tax unit). Uses `earned_income`
            # which follows the EITC convention of wages + self-employment.
            if p.earnings_credit.use_earnings_credit:
                earnings = person("earned_income", period)
                capped_earnings = min_(max_(earnings, 0), p.earnings_credit.cap)
                person_earnings_credit = capped_earnings * p.earnings_credit.rate
                earnings_credit_amount = tax_unit.sum(person_earnings_credit)
            else:
                earnings_credit_amount = 0

            return (
                taxpayer_amount
                + ctc_dependent_amount
                + other_dependent_amount
                + household_amount
                + earnings_credit_amount
            )

    def modify_parameters(parameters):
        # Append `flat_refundable_credit` to every existing transition of
        # `gov.irs.credits.refundable`. Snapshotting first avoids mutating
        # the list while we iterate it.
        refundable = parameters.gov.irs.credits.refundable
        transitions = [
            (entry.instant_str, list(entry.value)) for entry in refundable.values_list
        ]
        for instant_str, value in transitions:
            if "flat_refundable_credit" in value:
                continue
            refundable.update(
                start=instant(instant_str),
                value=value + ["flat_refundable_credit"],
            )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(flat_refundable_credit)
            self.modify_parameters(modify_parameters)

    return reform


def create_refundable_credit_conversion_reform(
    parameters, period, bypass: bool = False
):
    """Auto-application function for the refundable credit conversion reform."""
    if bypass:
        return create_refundable_credit_conversion()

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


refundable_credit_conversion = create_refundable_credit_conversion_reform(
    None, None, bypass=True
)
