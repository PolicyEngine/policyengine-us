from policyengine_us.model_api import *


class va_subtractions_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia adjusted gross income subtractions attributed to each person"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(person, period, parameters):
        # Virginia's "Worksheet for Determining Separate Virginia Adjusted Gross
        # Income" (Form 760 instructions, STEP 2) attributes each subtraction to
        # the spouse who received the income. This sums the same person-level
        # subtractions list that drives the tax-unit total (va_subtractions).
        # Tax-unit other subtractions are prorated by each spouse's share of
        # federal AGI; the per-person amounts sum to the tax-unit total unless
        # no member has positive federal AGI (in which case the tax-unit keeps
        # the subtraction, but nobody gets a share).
        p = parameters(period).gov.states.va.tax.income.subtractions
        person_subtractions = add(person, period, p.subtractions)
        # Prorate tax-unit other subtractions across spouses by federal AGI share.
        person_fagi = person("adjusted_gross_income_person", period)
        positive_fagi = max_(person_fagi, 0)
        total_federal_agi = person.tax_unit.sum(positive_fagi)
        prorate = where(
            total_federal_agi > 0,
            np.divide(
                positive_fagi,
                total_federal_agi,
                out=np.zeros_like(total_federal_agi, dtype=float),
                where=total_federal_agi > 0,
            ),
            0,
        )
        other_sub = person.tax_unit("va_other_subtractions", period) * prorate
        total_subtractions = person_subtractions + other_sub
        # Prevent negative subtractions from acting as additions.
        return max_(0, total_subtractions)
