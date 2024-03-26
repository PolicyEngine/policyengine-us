from policyengine_us.model_api import *


class nj_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey property tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2021/1040i.pdf#page=49"
        "https://www.nj.gov/treasury/taxation/pdf/other_forms/tgi-ee/2022/1040i.pdf#page=50"
        "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=52"
    )
    defined_for = "nj_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        # calculate credit amount
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        separate = filing_status == status.SEPARATE
        cohabitating = tax_unit("cohabitating_spouses", period)
        p = parameters(period).gov.states.nj.tax.income.credits.property_tax
        credit_amount = p.amount / (1 + separate * cohabitating)

        # taking credit if not taking deduction
        taking_deduction = tax_unit("nj_taking_property_tax_deduction", period)
        return credit_amount * ~taking_deduction
