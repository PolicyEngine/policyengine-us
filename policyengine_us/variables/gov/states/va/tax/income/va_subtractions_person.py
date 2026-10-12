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
        # subtractions list that drives the tax-unit total (va_subtractions), so
        # the per-person amounts sum to it exactly.
        p = parameters(period).gov.states.va.tax.income.subtractions
        total_subtractions = add(person, period, p.subtractions)
        # Prevent negative subtractions from acting as additions.
        return max_(0, total_subtractions)
