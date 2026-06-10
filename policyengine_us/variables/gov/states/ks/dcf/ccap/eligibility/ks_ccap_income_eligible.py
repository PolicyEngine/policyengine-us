from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class ks_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Kansas CCAP based on income"
    definition_period = MONTH
    defined_for = StateCode.KS
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/Current/keesm7540.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Appendix/F-1MonthlyFamilyIncomeandFamilyShareDeductionSchedule.pdf",
        "https://content.dcf.ks.gov/ees/keesm/implem_memo/2021_07_01_increaseto250percentnofs.html",
    )

    def formula(spm_unit, period, parameters):
        # KEESM 7540: a family is income eligible when monthly gross income is
        # within the F-1 schedule's "Income Limit" column, which DCF defines as
        # 85% of State Median Income for the family size (families above 85% SMI
        # are not eligible). The 250% FPL figure in the 2021 DCF memo is the
        # policy basis behind the schedule, not a separate operational
        # comparison, so the SMI ceiling is the sole binding income test.
        p = parameters(period).gov.states.ks.dcf.ccap.family_share
        income = spm_unit("ks_ccap_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        # CCAP requires a child, so the schedule starts at a family of 2;
        # families larger than the F-1 maximum use the largest column's values.
        capped_size = min_(size, p.max_family_size)
        # F-1 "Income Limit" = round-half-up(85% x monthly SMI for the size).
        # SMI is released each October for the upcoming federal fiscal year and
        # uprated thereafter; pin it to the release in effect at the start of the
        # benefit period (the figures DCF used to build the published schedule)
        # rather than the uprated current-period value. Note: DCF refreshes
        # the published F-1 each May, so from October through April the model
        # applies the newer SMI vintage a few months before DCF's printed
        # schedule catches up - a deliberate forward-modeling choice.
        year = period.start.year
        month = period.start.month
        smi_year = year if month >= 10 else year - 1
        smi_instant = f"{smi_year}-10-01"
        annual_smi = smi(capped_size, state, smi_instant, parameters)
        income_limit = np.floor(
            p.smi_income_limit_rate * annual_smi / MONTHS_IN_YEAR + 0.5
        )
        income_eligible = income <= income_limit
        # KEESM 7540: a family need not demonstrate financial need (the income
        # test) when someone in the household is a TANF recipient.
        is_tanf = spm_unit("is_tanf_enrolled", period)
        return is_tanf | income_eligible
