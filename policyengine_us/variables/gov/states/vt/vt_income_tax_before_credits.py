from policyengine_us.model_api import *

class vt_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont main income tax (before credits and supplemental tax)"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("vt_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values

        p = parameters(period).gov.states.vt.tax.income.main

        return select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.WIDOW,
                filing_status == status.SEPARATE,
            ],
            [
                p.single.calc(taxable_income),
                p.joint.calc(taxable_income),
                p.head_of_household.calc(taxable_income),
                p.widow.calc(taxable_income),
                p.separate.calc(taxable_income),
            ],
        )
