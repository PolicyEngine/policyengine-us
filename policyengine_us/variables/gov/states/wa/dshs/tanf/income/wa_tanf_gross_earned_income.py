from policyengine_us.model_api import *


class wa_tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington TANF gross earned income"
    unit = USD
    definition_period = MONTH
    reference = ("https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0170",)
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        # Aggregate person-level federal TANF gross earned income
        person = spm_unit.members
        person_earned = person("tanf_gross_earned_income", period)
        return spm_unit.sum(person_earned)
