from policyengine_us.model_api import *


class cdcc_qualified_care_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified care expenses before dependent care benefits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/21#b_2",
        "https://www.law.cornell.edu/uscode/text/26/129#e_1",
        "https://www.irs.gov/pub/irs-prior/f2441--2017.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/f2441--2025.pdf#page=2",
    )

    def formula(tax_unit, period, parameters):
        expenses = add(
            tax_unit, period, ["cdcc_qualifying_childcare_expenses", "care_expenses"]
        )
        has_qualifying_individual = tax_unit("count_cdcc_eligible", period) > 0
        return where(has_qualifying_individual, max_(expenses, 0), 0)
