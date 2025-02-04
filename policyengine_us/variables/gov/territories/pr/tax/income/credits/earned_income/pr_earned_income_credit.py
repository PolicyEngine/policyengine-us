from policyengine_us.model_api import *

# - computation:
#     - need: earned income, number of children
#     - (phase-in-rate.yaml[child] * earned income), max with the max credit[child]
#     - phase-out = 0
#     - if single,
#         - if earned income > single-threshold, phase_out = (earned income - single-threshold) * phase-out-rate[child]
#     - if married,
#         - if earned income > married-threshold, phase_out = (earned income - joint-threshold) * phase-out-rate[child]
#     - phase in - phase out, min 0

class pr_earned_income_credit(Variable):
    value_type = float
    entity = Person
    label = "Puerto Rico earned income credit amount"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/laws-of-puerto-rico/title-thirteen-taxation-and-finance/subtitle-17-internal-revenue-code-of-2011/part-ii-income-taxes/chapter-1007-credits-against-tax/subchapter-b-refundable-credits/30211-earned-income-credit"
    defined_for = "pr_earned_income_credit_eligible"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.credits.earned_income

        child_count = person.tax_unit("pr_earned_income_child_count", period)
        filing_status = person.tax_unit("filing_status", period)
        gross_income = person("pr_gross_income_person", period)

        # compute credit
        phase_in = min_(gross_income * p.phase_in_rate.calc(child_count), 
                        p.max_amount.calc(child_count))
        phase_out = 0

        # CHECK ME: what are the possible filing statuses? 
        phase_out_rate = p.phase_out.rate.calc(child_count)
        if filing_status == filing_status.possible_values.SINGLE:
            single_threshold = p.phase_out.threshold.single.calc(child_count)
            if gross_income > single_threshold:
                phase_out = (gross_income - single_threshold) * phase_out_rate
        else: # default to married filing status
            married_threshold = p.phase_out.threshold.joint.calc(child_count)
            if gross_income > married_threshold:
                phase_out = (gross_income - married_threshold) * phase_out_rate

        return max_(0, phase_in - phase_out)