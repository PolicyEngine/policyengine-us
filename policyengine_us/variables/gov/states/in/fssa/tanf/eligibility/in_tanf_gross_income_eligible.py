from policyengine_us.model_api import *


class in_tanf_gross_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana TANF gross income eligible"
    definition_period = MONTH
    reference = (
        "https://iar.iga.in.gov/latestArticle/470/10.3",
        "https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # Gross income test - family must have gross income below limit
        # Per 470 IAC 10.3-4-2 (Gross Income Test)
        # Calculate gross income using federal TANF baseline
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )
        p = parameters(period).gov.states["in"].fssa.tanf.income
        capped_size = min_(spm_unit("spm_unit_size", period), 10)
        return gross_income < p.gross_income_limit[capped_size]
