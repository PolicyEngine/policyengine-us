from policyengine_us.model_api import *


class pr_earned_income_credit(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Puerto Rico earned income credit"
    definition_period = YEAR
    reference = "https://hacienda.pr.gov/sites/default/files/schedule_ct_rev._jul_5_23_informative_-_instructions.pdf#page=2"
    defined_for = "pr_earned_income_credit_eligible"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.credits.earned_income

        child_count = person.tax_unit("pr_earned_income_child_count", period)
        filing_status = person.tax_unit("filing_status", period)
        gross_income = person("pr_gross_income_person", period)
        print(p.phase_in_rate.calc(child_count))
        # compute credit
        phase_in = min_(
            gross_income * p.phase_in_rate.calc(child_count),
            p.max_amount.calc(child_count),
        )
        print(p.max_amount.calc(child_count))
        phase_out = 0

        # CHECK ME: what are the possible filing statuses?
        phase_out_rate = p.phase_out.rate.calc(child_count)
        if filing_status == filing_status.possible_values.SINGLE:
            single_threshold = p.phase_out.threshold.single.calc(child_count)
            if gross_income > single_threshold:
                phase_out = (gross_income - single_threshold) * phase_out_rate
        else:  # default to married filing status
            married_threshold = p.phase_out.threshold.joint.calc(child_count)
            if gross_income > married_threshold:
                phase_out = (gross_income - married_threshold) * phase_out_rate

        return max_(0, phase_in - phase_out)
