from policyengine_us.model_api import *


class in_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.in.gov/fssa/dfr/files/2800.pdf",
        "https://wioaplans.ed.gov/node/67731",
        "https://iar.iga.in.gov/latestArticle/470/10.3",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # Get federal TANF earned income (includes employment + self-employment)
        # Apply Indiana's 75% disregard (only 25% counted)
        # Per WIOA State Plan and Policy Manual Chapter 2800
        p = parameters(period).gov.states["in"].fssa.tanf.income
        person = spm_unit.members
        gross_earned = person("tanf_gross_earned_income", period)
        counted_rate = 1 - p.earned_income_disregard
        return spm_unit.sum(gross_earned * counted_rate)
