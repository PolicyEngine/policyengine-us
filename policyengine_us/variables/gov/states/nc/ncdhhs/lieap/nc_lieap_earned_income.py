from policyengine_us.model_api import *


class nc_lieap_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "North Carolina LIEAP earned income per person"
    defined_for = StateCode.NC
    reference = (
        # Section 300.09 A (pages 10-11), Section 300.09 B.3 (pages 12-13) and
        # Section 300.10 (pages 15-17).
        "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=10",
        # FNS 350.01 D, high school student earnings (page 2).
        "https://policies.ncdhhs.gov/wp-content/uploads/fns-350-whose-income-is-counted.pdf#page=2",
        # FNS 300.02 sources of income chart: college work study (page 5),
        # student earned income (page 21), wages and work study (page 26).
        "https://policies.ncdhhs.gov/wp-content/uploads/fns-300-sources-of-income.pdf#page=5",
        # FNS 315.09, college work-study (page 8).
        "https://policies.ncdhhs.gov/wp-content/uploads/fns-315-special-budgeting-income.pdf#page=8",
        # FY2026 state plan, item 1.9 countable income checklist (page 6).
        "https://liheapch.acf.gov/docs/2026/state-plans/NC_Plan_2026.pdf#page=6",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.lieap
        snap_unearned = parameters(period).gov.usda.snap.income.sources.unearned
        # Section 300.09 A takes countable income types from the FNS manual.
        # FNS 350.01 D.1 excludes earned income of K-12 students aged 17 or
        # younger who do not head the unit; FNS 300.02 and 315.09 exclude Title IV
        # work-study pay. The state plan's section 1.9 checklist marks child
        # earnings and work-study income as countable without those exceptions.
        # NOTE: the federal variable does not test head-of-unit status and
        # excludes all earnings of a federal work-study participant.
        countable = person("snap_countable_earner", period.first_month)
        # Existing net business and farm income approximates receipts less allowed
        # costs. No second business-expense deduction or new input is introduced.
        total = 0
        for source in p.earned_income_sources:
            amount = max_(person(source, period), 0)
            # Section 300.09 B.3 includes rental income in the work deduction.
            # It is on the SNAP unearned list, so the earner exclusions above
            # do not apply to it and it is counted in full.
            if source in snap_unearned:
                total = total + amount
            else:
                total = total + amount * countable
        return total
