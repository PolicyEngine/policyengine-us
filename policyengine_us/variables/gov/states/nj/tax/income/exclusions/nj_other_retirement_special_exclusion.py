from policyengine_us.model_api import *


class nj_other_retirement_special_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey Other Retirement Special Exclusion"
    unit = USD
    documentation = "New Jersey other retirement special exclusion"
    definition_period = YEAR
    reference = (
        "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21",
        "https://law.justia.com/codes/new-jersey/2022/title-54a/section-54a-6-15/",
    )
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # If filer (and spouse, if joint) are never eligible for social security benefits, they are eligible for special exclusion.
        # We will infer that if above age 70 with no social seurity benefits, then eligible.
        # Get the pension/retirement exclusion portion of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income.exclusions.retirement

        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        joint = filing_status == status.JOINT

        social_security = person("social_security", period)
        head_social_security = tax_unit.sum(where(is_head, social_security, 0))
        spouse_social_security = tax_unit.sum(
            where(is_spouse, social_security, 0)
        )

        head_age_eligible = (
            tax_unit("age_head", period) >= p.latest_age_social_security_start
        )
        head_eligible = head_age_eligible & (head_social_security == 0)
        spouse_age_eligible = (
            tax_unit("age_spouse", period)
            >= p.latest_age_social_security_start
        )
        spouse_eligible = spouse_age_eligible & (spouse_social_security == 0)

        eligible = where(
            joint,
            head_eligible & spouse_eligible,
            head_eligible,
        )

        return p.special_exclusion.amount[filing_status] * eligible
