from policyengine_us.model_api import *


class ky_liheap_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Kentucky LIHEAP countable household income"
    defined_for = StateCode.KY
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/KY_Plan_2026.pdf#page=5,6,7,34",
        "https://apps.legislature.ky.gov/law/kar/titles/921/004/116/",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ky.dcbs.liheap
        person = spm_unit.members
        # Annual income divided by twelve approximates the calendar month before
        # application. SPM units approximate the energy-purchasing household.
        adult = person("age", period) >= p.earned_income_age
        # Use existing net business and farm income, without another business
        # deduction. 921 KAR 4:116 Section 1(8) counts gross income received, so
        # each earned and unearned source is floored at zero and a loss in one
        # source cannot offset another.
        earned = (
            max_(person("employment_income", period), 0)
            + max_(person("self_employment_income", period), 0)
            + max_(person("sstb_self_employment_income", period), 0)
            + max_(person("farm_operations_income", period), 0)
        ) * adult
        unearned = 0
        for source in p.unearned_income_sources:
            unearned = unearned + max_(person(source, period), 0)
        # Reported Part B premiums approximate the Medicare deduction from SSA;
        # modeled premium liability does not establish an actual withholding.
        ssa = max_(
            person("social_security", period)
            - person("medicare_part_b_premiums_reported", period),
            0,
        )
        # Detailed excluded WIA/work-study earnings, jury duty, settlements,
        # other insurance payments, royalties, deposits, and non-taxable refunds
        # cannot be isolated with existing inputs. Do not add new inputs for this
        # draft.
        # The annual tanf aggregate includes ky_ktap and applies take-up; ky_ktap
        # alone represents monthly entitlement and would count benefits a
        # nonrecipient could get.
        return spm_unit.sum(earned + unearned + ssa) + spm_unit("tanf", period)
