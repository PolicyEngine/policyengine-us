from policyengine_us.model_api import *


class nc_lieap_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "North Carolina LIEAP earned income per person"
    defined_for = StateCode.NC
    reference = (
        "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=10,11,12,13,15,16,17",
        "https://policies.ncdhhs.gov/wp-content/uploads/fns-350-whose-income-is-counted.pdf#page=2",
        "https://policies.ncdhhs.gov/wp-content/uploads/fns-300-sources-of-income.pdf#page=5,21,26",
        "https://policies.ncdhhs.gov/wp-content/uploads/fns-315-special-budgeting-income.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/state-plans/NC_Plan_2026.pdf#page=6",
    )

    def formula(person, period, parameters):
        # Section 300.09 A takes countable income types from the FNS manual.
        # FNS 350.01 D.1 excludes earned income of K-12 students aged 17 or
        # younger who do not head the unit; FNS 300.02 and 315.09 exclude Title IV
        # work-study pay. The state plan's section 1.9 checklist marks child
        # earnings and work-study income as countable without those exceptions.
        # NOTE: the federal variable does not test head-of-unit status and
        # excludes all earnings of a federal work-study participant.
        countable = person("snap_countable_earner", period.first_month)
        # Existing net self-employment income approximates receipts less allowed
        # costs. No second business-expense deduction or new input is introduced.
        earnings = max_(person("employment_income", period), 0) + max_(
            person("self_employment_income", period), 0
        )
        # Section 300.09 B.3 includes rental income in the work deduction.
        return earnings * countable + max_(person("rental_income", period), 0)
