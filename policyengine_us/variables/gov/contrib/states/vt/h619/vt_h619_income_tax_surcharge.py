from policyengine_us.model_api import *


class vt_h619_income_tax_surcharge(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont H.619 income tax surcharge"
    unit = USD
    reference = "https://legislature.vermont.gov/Documents/2026/Docs/BILLS/H-0619/H-0619%20As%20Introduced.pdf"
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.contrib.states.vt.h619.income_tax_surcharge

        # Not a marginal tax - applies to FULL AGI once threshold is crossed
        agi = tax_unit("adjusted_gross_income", period)
        meets_threshold = agi >= p.agi_threshold
        surcharge = where(meets_threshold, agi * p.rate, 0)

        return where(p.in_effect, surcharge, 0)
