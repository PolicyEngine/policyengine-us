from policyengine_us.model_api import *


class ia_tanf_gross_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa TANF gross income limit"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28",
        "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-27",
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.hhs.tanf
        gl = p.income.gross_income_limit
        unit_size = spm_unit("spm_unit_size", period)
        base = gl.amount.calc(unit_size)
        additional = (
            max_(unit_size - p.max_unit_size, 0) * gl.additional_person
        )
        return base + additional
