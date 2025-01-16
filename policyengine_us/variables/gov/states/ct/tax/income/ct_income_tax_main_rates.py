from policyengine_us.model_api import *


class ct_income_tax_main_rates(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut income tax from main rate structure"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("ct_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        p = parameters(period).gov.states.ct.tax.income.rates
        return select(
            [
                filing_status == status.JOINT,
                filing_status == status.SEPARATE,
                filing_status == status.SURVIVING_SPOUSE,
                filing_status == status.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.joint.calc(taxable_income),
                p.separate.calc(taxable_income),
                p.surviving_spouse.calc(taxable_income),
                p.head_of_household.calc(taxable_income),
            ],
            default=p.single.calc(taxable_income),
        )
