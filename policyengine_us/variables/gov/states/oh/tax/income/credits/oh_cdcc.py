from policyengine_us.model_api import *


class oh_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio child and dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.credits.cdcc

        agi = tax_unit("oh_agi", period)
        us_cdcc = tax_unit("cdcc", period)

        rate = p.match.calc(agi)
        # qualify for full CDCC amount when AGI < 20_000
        # qualify for 25% percent of CDCC when 20000 <= AGI < 40_000
        # not qualify when AGI >= 40_000
        return rate * us_cdcc
