from policyengine_us.model_api import *


class pa_liheap_benefit_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Pennsylvania LIHEAP annual income for benefit determination"
    defined_for = StateCode.PA
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2026-liheap-state-plan.pdf#page=42",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dhs/documents/services/assistance/documents/heating-assistance_liheap/2027-liheap-state-plan.pdf#page=39",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.liheap.income
        income = spm_unit("pa_liheap_income", period)
        wages = add(spm_unit, period, ["pa_liheap_countable_employment_income"])
        # Section 601.41(2) applies only to benefit determination. Eligibility
        # uses income before this wage-only disregard; business is not wages.
        return max_(income - p.benefit_wage_disregard * wages, 0)
