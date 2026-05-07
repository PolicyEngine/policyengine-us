from policyengine_us.model_api import *


class ca_tanf_countable_income_applicant(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Countable Income for Eligibility"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=11450.12."

    def formula(spm_unit, period, parameters):
        countable_earned_from_people = add(
            spm_unit,
            period,
            ["ca_tanf_earned_income_after_disregard_person"],
        )
        gross_earned = spm_unit("ca_tanf_earned_income", period)
        gross_earned_from_people = add(
            spm_unit, period, ["ca_tanf_earned_income_person"]
        )
        monthly_gross_earned = gross_earned / period.size_in_months
        legacy_countable_earned = sum(
            max_(
                monthly_gross_earned
                - parameters(
                    subperiod
                ).gov.states.ca.cdss.tanf.cash.income.disregards.applicant.flat,
                0,
            )
            for subperiod in period.get_subperiods(MONTH)
        )
        # Preserve per-person disregards for modeled earnings, but keep direct
        # aggregate overrides usable in tests/debugging when person inputs are absent
        # or intentionally out of sync.
        countable_earned = where(
            gross_earned != gross_earned_from_people,
            legacy_countable_earned,
            countable_earned_from_people,
        )
        db_unearned = spm_unit("ca_tanf_db_unearned_income", period)
        other_unearned = spm_unit("ca_tanf_other_unearned_income", period)

        return countable_earned + db_unearned + other_unearned
