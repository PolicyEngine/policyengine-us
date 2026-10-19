from policyengine_us.model_api import *


class oh_income_tax_exempt(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Ohio income tax exempt"
    defined_for = StateCode.OH
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.02",
    )

    def formula(tax_unit, period, parameters):
        # ORC 5747.02(A)(3): no tax on income other than taxable business
        # income if that balance is "equal to or less than" the threshold.
        taxable_nonbusiness_income = tax_unit("oh_taxable_nonbusiness_income", period)
        p = parameters(period).gov.states.oh.tax.income
        return taxable_nonbusiness_income <= p.agi_threshold
