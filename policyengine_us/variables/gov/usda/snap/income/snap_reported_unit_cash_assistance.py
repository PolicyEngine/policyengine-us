from policyengine_us.model_api import *
from policyengine_us.tools.general import has_input_for_period


class snap_reported_unit_cash_assistance(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "CAPI and AABD cash supplied as unit income for SNAP"
    unit = USD
    reference = "https://www.ecfr.gov/current/title-7/section-273.9#p-273.9(b)(2)(i)"

    def formula(spm_unit, period):
        # CAPI and AABD normally count as income of their recipients. A user
        # can instead supply the entire grant at SPM unit level, which has
        # no recipient assignment and replaces the calculated person amounts.
        simulation = spm_unit.simulation
        sources = []
        if has_input_for_period(simulation, "ca_capi", period.this_year):
            sources.append("ca_capi")
        if has_input_for_period(simulation, "il_aabd", period):
            sources.append("il_aabd")
        return add(spm_unit, period, sources) if sources else 0
