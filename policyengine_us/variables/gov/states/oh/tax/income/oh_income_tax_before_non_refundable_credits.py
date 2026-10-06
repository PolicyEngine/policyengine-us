from policyengine_us.model_api import *


class oh_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio income tax before credits"
    defined_for = StateCode.OH
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf"

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("oh_taxable_income", period)
        p = parameters(period).gov.states.oh.tax.income
        exempt = tax_unit("oh_income_tax_exempt", period)
        # The statute sets a base amount for each bracket. The marginal rates
        # reproduce it except where the statute leaves a step (2025, above
        # $100,000), which the base adjustment adds. "More than" the
        # threshold, so right=True keeps the threshold itself in the lower step.
        base_adjustment = p.base_adjustment.calc(taxable_income, right=True)
        return (p.rates.calc(taxable_income) + base_adjustment) * ~exempt
