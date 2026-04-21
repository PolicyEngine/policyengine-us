from policyengine_us.model_api import *


class pa_uc(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania unemployment compensation"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf",
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=133",
    )
    defined_for = "pa_uc_monetarily_eligible"

    def formula(person, period, parameters):
        # § 404(c) caps only the base compensation balance (MBA = WBR *
        # credit weeks up to 26), so partial-benefit claims can last beyond
        # 26 weeks until that balance is exhausted. Dependent allowances are
        # payable on valid claim weeks, including partial weeks, but only for
        # the claimant's weeks of entitlement.
        weekly_benefit_rate = person("pa_uc_weekly_benefit_rate", period)
        partial_benefit_credit = person("pa_uc_partial_benefit_credit", period)
        gross_weekly_earnings = person("pa_uc_gross_weekly_earnings", period)
        dependent_allowance = person("pa_uc_dependent_allowance", period)
        maximum_benefit_amount = person("pa_uc_maximum_benefit_amount", period)
        maximum_weeks = person("pa_uc_maximum_weeks", period)
        weeks_unemployed = person("pa_uc_weeks_unemployed", period)

        earnings_reduction = max_(gross_weekly_earnings - partial_benefit_credit, 0)
        weekly_base_payable = max_(weekly_benefit_rate - earnings_reduction, 0)
        base_benefits_paid = min_(
            weekly_base_payable * weeks_unemployed, maximum_benefit_amount
        )

        payable_week = gross_weekly_earnings < (
            weekly_benefit_rate + partial_benefit_credit
        )
        dependent_weeks = where(
            payable_week,
            min_(weeks_unemployed, maximum_weeks),
            0,
        )
        return base_benefits_paid + dependent_allowance * dependent_weeks
