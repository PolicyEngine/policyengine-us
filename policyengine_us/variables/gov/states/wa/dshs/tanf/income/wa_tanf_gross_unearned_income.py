from policyengine_us.model_api import *


class wa_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington TANF gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0162",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0025",
    )
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        # Aggregate person-level federal TANF gross unearned income
        person = spm_unit.members
        person_unearned = person("tanf_gross_unearned_income", period)
        return spm_unit.sum(person_unearned)
