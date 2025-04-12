from policyengine_us.model_api import *


class ok_federal_eitc_phase_in_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC phase-in rate for the Oklahoma EITC computation"
    unit = "/1"
    documentation = "Rate at which the EITC phases in with income."
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        child_count = tax_unit("eitc_child_count", period)
        eitc = parameters(f"2020-01-01").gov.irs.credits.eitc
        return eitc.phase_in_rate.calc(child_count)
