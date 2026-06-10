from policyengine_us.model_api import *


class ks_ccap_family_share(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Kansas CCAP family share deduction"
    definition_period = MONTH
    defined_for = "ks_ccap_eligible"
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/Current/keesm7540.htm",
        "https://content.dcf.ks.gov/ees/KEESM/Appendix/F-1MonthlyFamilyIncomeandFamilyShareDeductionSchedule.pdf",
    )

    def formula(spm_unit, period, parameters):
        # KEESM 7541 / Appendix F-1: the family share deduction is looked up from
        # the F-1 schedule by family size and the family's monthly gross income.
        # Families below 100% FPL owe $0; the deduction rises across the FPL
        # tiers up to the 85% SMI ceiling. KEESM 7541 assesses the deduction only
        # for "Income Eligible (Non-TANF) clients," so TANF recipients owe no
        # family share. We don't model the KEESM 2835 exceptions (e.g. child care
        # to prevent abuse/neglect) at the moment.
        p = parameters(period).gov.states.ks.dcf.ccap.family_share.deduction
        income = spm_unit("ks_ccap_countable_income", period)
        size = spm_unit("spm_unit_size", period.this_year)
        # CCAP requires a child, so the schedule starts at a family of 2;
        # families larger than 11 use the size-11 column.
        deduction = select(
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
                p.size_2.calc(income),
                p.size_3.calc(income),
                p.size_4.calc(income),
                p.size_5.calc(income),
                p.size_6.calc(income),
                p.size_7.calc(income),
                p.size_8.calc(income),
                p.size_9.calc(income),
                p.size_10.calc(income),
            ],
            default=p.size_11.calc(income),
        )
        is_tanf = spm_unit("is_tanf_enrolled", period)
        return where(is_tanf, 0, deduction)
