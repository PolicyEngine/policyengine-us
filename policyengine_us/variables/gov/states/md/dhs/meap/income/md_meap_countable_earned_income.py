from policyengine_us.model_api import *


class md_meap_countable_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Maryland MEAP countable earnings"
    unit = USD
    defined_for = StateCode.MD
    reference = ("https://regs.maryland.gov/us/md/exec/comar/07.03.21.04#E(3)",)
    documentation = (
        "Uses existing net business income without an additional expense deduction. "
        "MEAP depreciation add-backs are unsupported. Each source is floored at zero, "
        "so a loss in one source cannot offset another."
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.dhs.meap
        earned = 0
        for source in p.income.sources.earned:
            earned = earned + max_(person(source, period), 0)
        # COMAR 07.03.21.04E(3) excludes the employment income of a child
        # younger than 18 or of a full-time student.
        counted = (person("age", period) >= p.adult_age) & ~person(
            "is_full_time_student", period
        )
        return where(counted, earned, 0)
