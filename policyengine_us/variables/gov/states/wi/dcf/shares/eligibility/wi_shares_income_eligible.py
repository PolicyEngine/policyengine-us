from policyengine_us.model_api import *


class wi_shares_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wisconsin Shares income eligible"
    definition_period = MONTH
    defined_for = StateCode.WI
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=57",
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=58",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/III/155/1m/c",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wi.dcf.shares.income.limit
        countable_income = spm_unit("wi_shares_countable_income", period)
        enrolled = spm_unit("is_wi_shares_enrolled", period)
        # New applicants (and assistance groups closed for more than one
        # calendar month) are tested against 200% of the federal poverty
        # guideline (Section 6.1.1); enrolled assistance groups remain
        # eligible until income exceeds 85% of the state median income
        # (Section 6.1.2). spm_unit_fpg and hhs_smi are annual dollar amounts,
        # so reading them with the bare monthly period auto-divides them to
        # monthly values.
        monthly_fpg = spm_unit("spm_unit_fpg", period)
        monthly_smi = spm_unit("hhs_smi", period)
        initial_limit = monthly_fpg * p.initial_fpg_rate
        ongoing_limit = monthly_smi * p.ongoing_smi_rate
        income_limit = where(enrolled, ongoing_limit, initial_limit)
        return countable_income <= income_limit
