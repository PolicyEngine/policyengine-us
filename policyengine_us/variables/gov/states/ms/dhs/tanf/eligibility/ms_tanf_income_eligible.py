from policyengine_us.model_api import *


class ms_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Mississippi TANF income eligibility"
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = (
        "https://www.mdhs.ms.gov/wp-content/uploads/2018/02/MDHS_TANF-Eligibility-Flyer.pdf",
        "https://www.law.cornell.edu/regulations/mississippi/Miss-Code-tit-18-pt-19",
        "https://www.mdhs.ms.gov/help/tanf/applying-for-tanf/",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ms.dhs.tanf

        # Use federal baseline for gross income
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )

        # Get need standard based on household size (capped at table max)
        size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(size, p.need_standard.max_table_size).astype(int)
        need_standard = p.need_standard.amount[capped_size]

        # Gross income limit is 185% of need standard
        gross_income_limit = need_standard * p.income.gross_income_limit_rate

        return gross_income <= gross_income_limit
