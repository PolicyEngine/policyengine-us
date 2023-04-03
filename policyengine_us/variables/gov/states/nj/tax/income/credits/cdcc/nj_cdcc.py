from policyengine_us.model_api import *
import numpy as np


class nj_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey CDCC"
    documentation = "New Jersey Child and Dependent Care Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=44"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.tax.income.credits.cdcc.rate
        agi = tax_unit("adjusted_gross_income", period)
        federal_cdcc = tax_unit("cdcc", period)
        rate = p.calc(agi)
        return federal_cdcc * rate
