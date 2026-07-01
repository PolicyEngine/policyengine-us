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
        "https://www.azleg.gov/legtext/57leg/2R/bills/HB4168H.pdf#page=28",
    )

    def formula(tax_unit, period, parameters):
        # A.R.S. 43-1022(34) (HB 4168, TY2026+): "the amount of child and
        # dependent care expenses for a qualifying individual under section 21
        # of the internal revenue code paid or incurred ... that exceeds the
        # amount of the federal credit ... under section 21." The expense base
        # is cdcc_relevant_expenses, which applies the IRC 21 dollar and
        # earned-income limits and equals 0 when there is no qualifying
        # individual (count_cdcc_eligible == 0).
        expenses = tax_unit("cdcc_relevant_expenses", period)
        federal_credit = tax_unit("cdcc", period)
        return max_(expenses - federal_credit, 0)
