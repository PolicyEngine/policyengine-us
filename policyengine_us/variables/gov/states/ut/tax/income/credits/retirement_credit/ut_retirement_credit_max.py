from policyengine_us.model_api import *


class ut_retirement_credit_max(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah retirement credit maximum amount"
    unit = USD
    definition_period = YEAR
    reference = "https://incometax.utah.gov/credits/retirement-credit"
    defined_for = StateCode.UT

    def formula(tax_unit, period: Period, parameters):
        """
        This credit is an alternative to the social security benefits credit,
        but instead is based on a flat rate.
        """
        p = parameters(period).gov.states.ut.tax.income
        p_credit = p.credits.retirement
        person = tax_unit.members
        age = person("age", period)
        birth_year = -(age - period.start.year)
        # The credit is for the claimant and, on a joint return, the spouse;
        # a tax unit dependent is not a claimant on this return.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        meets_age_conditions = (birth_year <= p_credit.birth_year) & head_or_spouse
        max_value = p_credit.max * tax_unit.sum(meets_age_conditions)
        total_income = tax_unit("ut_total_income", period)
        # The head's and spouse's municipal bond interest, as Utah total
        # income leaves out a tax unit dependent's income.
        tax_exempt_interest = tax_unit_non_dep_add(
            tax_unit, period, ["tax_exempt_interest_income"]
        )
        modified_agi = total_income + tax_exempt_interest
        filing_status = tax_unit("filing_status", period)
        phase_out_income = max_(
            0, modified_agi - p_credit.phase_out.threshold[filing_status]
        )
        phase_out_reduction = phase_out_income * p_credit.phase_out.rate
        return max_(0, max_value - phase_out_reduction)
