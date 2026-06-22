from policyengine_us.model_api import *


class az_dependent_care_expense_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona dependent care expense subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = (
        "https://www.azleg.gov/ars/43/01022.htm",
        "https://www.azleg.gov/legtext/57leg/2R/bills/HB4168P.pdf",
    )

    def formula(tax_unit, period, parameters):
        # A.R.S. 43-1022(34) (HB 4168, TY2026+): the amount of child and
        # dependent care expenses under IRC 21 paid or incurred for the taxable
        # year that exceeds the amount of the federal credit received under
        # IRC 21. The bill sets no cap.
        expenses = tax_unit("tax_unit_childcare_expenses", period)
        federal_credit = tax_unit("cdcc", period)
        return max_(expenses - federal_credit, 0)
