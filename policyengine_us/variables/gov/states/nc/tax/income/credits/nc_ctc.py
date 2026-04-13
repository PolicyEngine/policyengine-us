from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    applied_state_non_refundable_credit,
)


class nc_ctc_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina credit for children"
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.ncdor.gov/taxes-forms/individual-income-tax/credit-children"
    )
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        ctc_qualifying_children = tax_unit("ctc_qualifying_children", period)
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.nc.tax.income.credits.ctc
        status = filing_status.possible_values
        credit_amount = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.JOINT,
                filing_status == status.SURVIVING_SPOUSE,
                filing_status == status.SEPARATE,
            ],
            [
                p.single.calc(income),
                p.head_of_household.calc(income),
                p.joint.calc(income),
                p.surviving_spouse.calc(income),
                p.separate.calc(income),
            ],
        )
        return ctc_qualifying_children * credit_amount


class nc_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina credit for children"
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.ncdor.gov/taxes-forms/individual-income-tax/credit-children"
    )
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        ordered_credits = parameters(
            period
        ).gov.states.nc.tax.income.credits.non_refundable
        return applied_state_non_refundable_credit(
            tax_unit,
            period,
            ordered_credits,
            "nc_income_tax_before_credits",
            "nc_ctc",
            "nc_ctc_potential",
        )
