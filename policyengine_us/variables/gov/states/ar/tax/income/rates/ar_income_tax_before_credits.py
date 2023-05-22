from policyengine_us.model_api import *
import numpy as np


class ar_income_tax_before_credits(Variable):
    value_type = int
    entity = TaxUnit
    label = "Arkansas income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        ""
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("ar_taxable_income", period)
        p = parameters(period).gov.states.ar.tax.income.rates
        ar_income_tax_before_credits = p.calc(taxable_income)
        return int(np.floor(ar_income_tax_before_credits + 0.5))