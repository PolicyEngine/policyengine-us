from policyengine_us.model_api import *


class ks_liheap_income_band(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Kansas LIEAP one-month income band"
    documentation = "Benefit matrix income band (1-4) from one-month gross countable income, taken as one twelfth of annual countable income."
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/KS_BenefitMatrix_2026.pdf#page=1",
        "https://content.dcf.ks.gov/ees/keesm/current/keesm13200.htm",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ks.dcf.liheap.payment
        income = spm_unit("ks_liheap_countable_income", period)
        monthly_income = max_(income, 0) / MONTHS_IN_YEAR
        return p.income_band.calc(monthly_income)
