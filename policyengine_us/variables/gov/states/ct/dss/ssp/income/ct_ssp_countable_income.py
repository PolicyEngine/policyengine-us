from policyengine_us.model_api import *


class ct_ssp_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Connecticut SSP countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = (
        "https://www.ctdssmap.com/CTPortal/Information/Get/UPM#5030.10",
        "https://www.ctdssmap.com/CTPortal/Information/Get/UPM#5030.15",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/ct.html",
    )

    def formula(person, period, parameters):
        # Per UPM 5030.10/5030.15: Countable = (unearned - disregard) + (earned - disregard).
        # SSI payments are included in unearned income.
        total_unearned = add(
            person,
            period,
            [
                "ssi_unearned_income",
                "ssi",
                "ssi_unearned_income_deemed_from_ineligible_spouse",
            ],
        )
        unearned_disregard = person("ct_ssp_unearned_income_disregard", period)
        countable_unearned = max_(total_unearned - unearned_disregard, 0)

        gross_earned = add(
            person,
            period,
            [
                "ssi_earned_income",
                "ssi_earned_income_deemed_from_ineligible_spouse",
            ],
        )
        earned_disregard = person("ct_ssp_earned_income_disregard", period)
        countable_earned = max_(gross_earned - earned_disregard, 0)

        return countable_unearned + countable_earned
