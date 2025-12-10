from policyengine_us.model_api import *


class mn_k12_education_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Minnesota K-12 Education Credit"
    definition_period = YEAR
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0674",
        "https://www.revenue.state.mn.us/sites/default/files/2025-12/m1ed-25.pdf",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.mn.tax.income.credits.k12_education
        # Check eligibility - not available for married filing separately
        filing_status = tax_unit("filing_status", period)
        is_separate = filing_status == filing_status.possible_values.SEPARATE
        # Count qualifying K-12 children
        k12_children = tax_unit("mn_k12_qualifying_children", period)
        # Check income limit based on number of children
        agi = tax_unit("adjusted_gross_income", period)
        # Income limit = base + additional * max(0, children - child_threshold)
        income_limit = p.income_limit.base + p.income_limit.additional * max_(
            0, k12_children - p.income_limit.child_threshold
        )
        income_eligible = agi < income_limit
        # Eligible if: not married filing separately, has qualifying children,
        # and income is below the limit
        return ~is_separate & income_eligible & (k12_children > 0)
