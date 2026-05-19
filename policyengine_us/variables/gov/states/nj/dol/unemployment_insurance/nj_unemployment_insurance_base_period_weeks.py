from policyengine_us.model_api import *


class nj_unemployment_insurance_base_period_weeks(Variable):
    value_type = int
    entity = Person
    label = "New Jersey unemployment insurance qualifying base weeks in the base period"
    unit = "week"
    documentation = (
        "Count of base-period weeks that already satisfy New Jersey's "
        "base-week earnings threshold (N.J.S.A. 43:21-19(t): a week in which "
        "the worker earned at least 20 times the state hourly minimum wage; "
        "$310/week in 2026, $303/week in 2025). Callers should pre-filter raw "
        "weeks using the applicable per-week threshold before inputting this "
        "count. Phase-1 scope: the regular and alternate base periods defined "
        "in N.J.S.A. 43:21-19(c) are not derived in-model."
    )
    definition_period = YEAR
    reference = "https://www.nj.gov/labor/myunemployment/assets/pdfs/UI_statute.pdf"
    defined_for = StateCode.NJ
