from policyengine_us.model_api import *


class ne_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Nebraska LIHEAP regular heating assistance eligibility"
    defined_for = StateCode.NE
    reference = "https://rules.nebraska.gov/rules?agencyId=37&titleId=231"

    def formula_2026(spm_unit, period, parameters):
        income_eligible = spm_unit("ne_liheap_income_eligible", period)
        # A positive heating bill demonstrates responsibility for energy
        # costs. Heat included in rent can also qualify, but rent alone does
        # not establish exposure to energy-price increases (476 NAC 1-004.06).
        # That vulnerability and administrative disqualifications are not
        # identifiable from existing inputs; no new inputs are introduced.
        responsible = spm_unit("heating_expense", period) > 0
        return income_eligible & responsible
