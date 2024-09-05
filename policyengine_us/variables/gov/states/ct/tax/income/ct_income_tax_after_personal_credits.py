from policyengine_us.model_api import *


class ct_income_tax_after_personal_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut income tax after personal tax credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("ct_taxable_income", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        p = parameters(period).gov.states.ct.tax.income.rates
        itax_before_personal_credits = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.SEPARATE,
                filing_status == status.SURVIVING_SPOUSE,
                filing_status == status.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.single.calc(taxable_income),
                p.joint.calc(taxable_income),
                p.separate.calc(taxable_income),
                p.surviving_spouse.calc(taxable_income),
                p.head_of_household.calc(taxable_income),
            ],
        )
        add_back = tax_unit("ct_income_tax_phase_out_add_back", period)
        tax_recapture = tax_unit("ct_income_tax_recapture", period)
        total = itax_before_personal_credits + add_back + tax_recapture
        personal_credit_rate = tax_unit("ct_personal_credit_rate", period)
        personal_credit_amount = personal_credit_rate * total
        return max_(0, total - personal_credit_amount)
