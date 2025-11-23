from policyengine_us.model_api import *


class in_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana TANF income eligible"
    definition_period = MONTH
    reference = (
        "https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/",
        "https://iga.in.gov/laws/2023/ic/titles/12",
        "https://iar.iga.in.gov/latestArticle/470/10.3",
    )
    defined_for = StateCode.IN

    def formula(spm_unit, period, parameters):
        # Indiana uses both gross and net income tests
        # Per 470 IAC 10.3-4 (Fiscal Eligibility Requirements)

        assistance_unit_size = spm_unit("in_tanf_assistance_unit_size", period)
        p = parameters(period).gov.states["in"].fssa.tanf.income

        # Gross income test
        gross_income = spm_unit("tanf_gross_income", period)
        capped_size = min_(assistance_unit_size, 10)
        gross_limit = p.gross_income_limit[capped_size]
        gross_eligible = gross_income < gross_limit

        # Net income test
        net_income = spm_unit("in_tanf_countable_income", period)
        net_limit = p.net_income_limit[capped_size]
        net_eligible = net_income < net_limit

        # Must pass both tests
        return gross_eligible & net_eligible
