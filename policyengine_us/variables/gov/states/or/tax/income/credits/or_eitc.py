from policyengine_us.model_api import *


class or_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "OR EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=18",
        "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2025.pdf#page=22",
        "https://www.oregonlegislature.gov/bills_laws/ors/ors315.html",  # Subsection 315.266
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        # Grab federal EITC.
        federal_eitc = tax_unit("eitc", period)
        # Check if the tax unit has a young child to qualify for a higher rate.
        person = tax_unit.members
        p = parameters(period).gov.states["or"].tax.income.credits.eitc
        # ORS 315.266 gives the higher rate to a taxpayer "with a dependent
        # under the age of three" (Form OR-40 instructions: 9 percent with "no
        # dependents"). A return on which a filer can be claimed as a
        # dependent has no dependents (IRC 152(b)(1)), unless the would-be
        # claimant meets the filing exception; it keeps the ordinary rate on
        # its federal credit.
        dependent_filer = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        young_child = (
            (person("age", period) < p.old_child_age)
            & person("is_tax_unit_dependent", period)
            & ~dependent_filer
        )
        # Re-aggregate to the tax unit level.
        has_young_child = tax_unit.any(young_child)
        # Multiply by the relevant factor.
        rate = where(has_young_child, p.match.has_young_child, p.match.no_young_child)
        return federal_eitc * rate
