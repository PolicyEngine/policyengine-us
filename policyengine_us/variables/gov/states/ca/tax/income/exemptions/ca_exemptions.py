from policyengine_us.model_api import *


def ca_personal_aged_blind_exemption_count(tax_unit, period, p, filing_status):
    """Number of personal, blind and senior exemption credits.

    A filer whom another taxpayer can claim as a dependent gets no personal,
    blind or senior credit (RTC 17054). The Form 540 line 7 instructions
    enter 0 for a single, separate or head of household filer who can be
    claimed and, on a joint return, 1 when only one spouse can be claimed and
    0 when both can; lines 8 and 9 say "Do not claim this credit if someone
    else can claim you as a dependent".
    """
    person = tax_unit.members
    filer = person("is_tax_unit_head_or_spouse", period)
    claimed = person("claimed_as_dependent_on_another_return", period)
    dependent_elsewhere = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
    personal_exemption_count = where(
        dependent_elsewhere,
        tax_unit("head_spouse_count_not_dependent_elsewhere", period),
        p.personal_scale[filing_status],
    )
    claimed_aged_blind_count = tax_unit.sum(
        (filer & claimed)
        * (person("is_irs_aged", period).astype(int) + person("is_blind", period))
    )
    aged_blind_count = tax_unit("aged_blind_count", period) - claimed_aged_blind_count
    return personal_exemption_count + aged_blind_count


class ca_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA Exemptions"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540.pdf",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17054",
        # Form 540 lines 6-10 instructions.
        "https://www.ftb.ca.gov/forms/2025/2025-540-booklet.pdf#page=12",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.exemptions
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)

        # calculating phase out amount per credit
        over_agi_threshold = max_(0, agi - p.phase_out.start[filing_status])
        increments = np.ceil(over_agi_threshold / p.phase_out.increment[filing_status])
        exemption_reduction = increments * p.phase_out.amount

        # Personal, blind and senior exemptions
        personal_aged_blind_exemption_count = ca_personal_aged_blind_exemption_count(
            tax_unit, period, p, filing_status
        )
        personal_aged_blind_exemption = max_(
            0,
            personal_aged_blind_exemption_count * (p.amount - exemption_reduction),
        )

        # Dependent exemptions: the dependents must be those claimed on the
        # federal return, and a return on which the filer (or, if joint,
        # either spouse) can be claimed has none (IRC 152(b)(1)).
        dependent_elsewhere = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        dependents = where(
            dependent_elsewhere, 0, tax_unit("tax_unit_dependents", period)
        )
        dependent_exemptions = max_(
            0, dependents * (p.dependent_amount - exemption_reduction)
        )

        # total exemptions
        return personal_aged_blind_exemption + dependent_exemptions
