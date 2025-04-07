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
        amount = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.JOINT,
                filing_status == statuses.SURVIVING_SPOUSE,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.single.calc(federal_agi, right=True),
                p.separate.calc(federal_agi, right=True),
                p.joint.calc(federal_agi, right=True),
                p.surviving_spouse.calc(federal_agi, right=True),
                p.head_of_household.calc(federal_agi, right=True),
            ],
        )
        # calculate number of eligible children
        children = tax_unit("ctc_qualifying_children", period)
        # calculate NC child deduction
        return amount * children
