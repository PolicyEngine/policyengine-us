from policyengine_us.model_api import *


class pa_uc_weekly_payable(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation weekly payable amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=22",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=137",
    )
    defined_for = "pa_uc_monetarily_eligible"

    def formula(person, period, parameters):
        # § 4(u): a claimant is "unemployed" for a week only when earnings are
        # less than WBR + PBC. § 404(e)(3) pays the dependent allowance only
        # "for each week that he is entitled to benefits." When earnings reach
        # or exceed WBR + PBC, the claimant is not unemployed and receives no
        # benefits (base or dependent allowance).
        wbr = person("pa_uc_weekly_benefit_rate", period)
        pbc = person("pa_uc_partial_benefit_credit", period)
        earnings = person("pa_uc_gross_weekly_earnings", period)
        dependent_allowance = person("pa_uc_dependent_allowance", period)
        earnings_reduction = max_(earnings - pbc, 0)
        payable_wbr = max_(wbr - earnings_reduction, 0)
        is_unemployed_this_week = earnings < (wbr + pbc)
        dep = where(is_unemployed_this_week, dependent_allowance, 0)
        return payable_wbr + dep
