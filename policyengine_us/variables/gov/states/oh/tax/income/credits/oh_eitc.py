from policyengine_us.model_api import *


class oh_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Earned Income Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.71",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=21",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        match = parameters(period).gov.states.oh.tax.income.credits.eitc.rate
        return federal_eitc * match
