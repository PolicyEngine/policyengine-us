from policyengine_us.model_api import *


class id_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Idaho LIHEAP regular heating assistance"
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        # PDF pages 8-9
        "https://liheapch.acf.gov/docs/2026/state-plans/ID_Plan_2026.pdf#page=8",
        "https://adminrules.idaho.gov/rules/current/16/160308.pdf#page=5",
        # IDAPA 16.04.14.001.02 and 152.02, in force for all of FY2026 heating.
        # PDF pages 3, 6
        "https://web.archive.org/web/20250910171431id_/https://adminrules.idaho.gov/rules/current/16/160414.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.dhw.liheap.payment
        income_eligible = spm_unit("id_liheap_income_eligible", period)
        cost = spm_unit("id_liheap_estimated_heating_cost", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        # Plan 2.3 requires the household to pay for heat. has_heating_expense
        # reads the primary fuel's bill, or can be set directly; the bill does
        # not set the amount.
        pays_for_heat = spm_unit("has_heating_expense", period)
        # Heat in rent stands for no specific heating-cost obligation; a
        # designated heat charge within the rent has no input. That base is
        # zero from FY2026, when plan 2.5 makes these households ineligible.
        # Other subsidized tenants paying for heat follow the general chart.
        return income_eligible & where(
            heat_in_rent, p.rent > 0, (cost > 0) & pays_for_heat
        )
