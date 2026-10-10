from policyengine_us.model_api import *


class traditional_ira_deduction(Variable):
    value_type = float
    entity = Person
    label = "Traditional IRA deduction"
    documentation = (
        "The IRC 219 deduction for traditional IRA contributions. For the head "
        "and spouse it is the deduction on this tax return. For a tax unit "
        "dependent it is the deduction on the dependent's own return, which "
        "the filers' above-the-line total leaves out."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#a",
        "https://www.law.cornell.edu/uscode/text/26/219#b_1",
        "https://www.law.cornell.edu/uscode/text/26/219#c",
        "https://www.law.cornell.edu/uscode/text/26/219#g",
        "https://www.law.cornell.edu/uscode/text/26/408#o_2",
    )

    def formula(person, period, parameters):
        compensation = person("ira_compensation", period)
        filer = person("is_tax_unit_head_or_spouse", period)
        joint = person.tax_unit("tax_unit_is_joint", period)
        total_compensation = person.tax_unit.sum(compensation * filer)
        spouse_compensation = max_(0, total_compensation - compensation)
        contributions = person("traditional_ira_contributions", period)
        roth_contributions = person("roth_ira_contributions", period)
        retirement = parameters(period).gov.irs.gross_income.retirement_contributions
        catch_up = person("age", period) >= retirement.catch_up.age_threshold
        dollar_limit = retirement.limit.ira + catch_up * retirement.catch_up.limit.ira
        # Section 219(c) subtracts deductible and designated nondeductible
        # traditional contributions, plus any Roth contributions. Section
        # 408(o)(2) caps designated traditional amounts; excess Roth amounts
        # still consume the spouse's compensation under section 219(c).
        # Only the higher earner's allowance is needed for the lower earner.
        compensation_consumed = min_(
            max_(0, contributions), min_(compensation, dollar_limit)
        ) + max_(0, roth_contributions)
        spouse_contributions = max_(
            0,
            person.tax_unit.sum(compensation_consumed * filer) - compensation_consumed,
        )
        lower_earning_spouse = joint & filer & (compensation < spouse_compensation)
        available_compensation = where(
            lower_earning_spouse,
            compensation + max_(0, spouse_compensation - spouse_contributions),
            compensation,
        )
        # Applying the cap here also covers directly supplied actual contributions.
        limit = min_(
            available_compensation, person("ira_219g_deductible_limit", period)
        )
        claimant = person("is_tax_unit_head", period) | (
            person("is_tax_unit_spouse", period) & joint
        )
        filer_deduction = max_(0, min_(contributions, limit)) * claimant
        # A tax unit dependent's deduction is on the dependent's own return.
        # It is recorded on the dependent so that person-level consumers see
        # it; the filers' above-the-line total sums the head and spouse only.
        return where(
            person("is_tax_unit_dependent", period),
            person("dependent_traditional_ira_deduction", period),
            filer_deduction,
        )
