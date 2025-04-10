from policyengine_us.model_api import *


class ok_federal_eitc_phase_out_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal EITC phase-out rate for the Oklahoma EITC computation"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/"
    )
    defined_for = StateCode.OK

    def formula(tax_unit, period, parameters):
        eitc = parameters(f"2020-01-01").gov.irs.credits.eitc
        num_children = tax_unit("eitc_child_count", period)
        return eitc.phase_out.rate.calc(num_children)
