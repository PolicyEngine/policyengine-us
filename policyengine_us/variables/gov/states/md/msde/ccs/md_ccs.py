from policyengine_us.model_api import *


class md_ccs(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Maryland Child Care Scholarship (CCS) benefit amount"
    definition_period = MONTH
    defined_for = "md_ccs_eligible"
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/13A.14.06.11",
        "https://earlychildhood.marylandpublicschools.org/families/child-care-scholarship-program/child-care-scholarship-rates",
    )

    def formula(spm_unit, period, parameters):
        weekly_copay = spm_unit("md_ccs_weekly_copay", period)
        annual_copay = weekly_copay * WEEKS_IN_YEAR

        actual_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period.this_year
        )

        person = spm_unit.members
        is_eligible_child = person("md_ccs_eligible_child", period)
        weekly_rate = person("md_ccs_payment_rate", period)
        weekly_to_annual = WEEKS_IN_YEAR
        max_reimbursement = (
            spm_unit.sum(weekly_rate * is_eligible_child) * weekly_to_annual
        )

        uncapped_benefit = max_(actual_expenses - annual_copay, 0)
        return min_(uncapped_benefit, max_reimbursement) / MONTHS_IN_YEAR
