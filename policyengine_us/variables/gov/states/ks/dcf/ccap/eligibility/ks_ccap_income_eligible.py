from policyengine_us.model_api import *


class ks_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Kansas CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.KS
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/Current/keesm7540.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Appendix/F-1MonthlyFamilyIncomeandFamilyShareDeductionSchedule.pdf",
    )

    def formula(spm_unit, period, parameters):
        # KEESM 7540: a family is income eligible when gross income is within the
        # income limits "established annually by the agency," which the rule
        # delegates entirely to the Appendix F-1 schedule. The F-1 "Income Limit"
        # column is 85% of State Median Income for every family size (the F-1
        # header states families above 85% SMI are not eligible); the 250% FPL
        # figure in the 2021 DCF memo is the policy basis used to set the
        # schedule, not a separate operational comparison, so F-1 is the sole
        # binding income ceiling.
        p = parameters(period).gov.states.ks.dcf.ccap.family_share.income_limit
        countable_income = spm_unit("ks_ccap_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        # CCAP requires a child, so the schedule starts at a family of 2;
        # families larger than 11 use the size-11 column.
        income_limit = select(
            [
                size <= 2,
                size == 3,
                size == 4,
                size == 5,
                size == 6,
                size == 7,
                size == 8,
                size == 9,
                size == 10,
            ],
            [
                p.size_2,
                p.size_3,
                p.size_4,
                p.size_5,
                p.size_6,
                p.size_7,
                p.size_8,
                p.size_9,
                p.size_10,
            ],
            default=p.size_11,
        )
        income_eligible = countable_income <= income_limit
        # KEESM 7540: a family need not demonstrate financial need (the income
        # test) when someone in the household is a TANF recipient, so TANF
        # families are income eligible regardless of the F-1 ceiling.
        is_tanf = spm_unit("is_tanf_enrolled", period)
        return is_tanf | income_eligible
