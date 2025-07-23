from policyengine_us.model_api import *


class nc_child_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina child deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        # calculate deduction amount per eligible child
        federal_agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        p = parameters(period).gov.states.nc.tax.income.deductions.child
        amount = select_filing_status_value(
            filing_status,
            p,
            federal_agi,
            right=True,
        )
        # calculate number of eligible children
        children = tax_unit("ctc_qualifying_children", period)
        # calculate NC child deduction
        return amount * children
