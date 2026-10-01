from policyengine_us.model_api import *


class md_meap_countable_earned_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Maryland MEAP countable earnings"
    unit = USD
    defined_for = StateCode.MD
    reference = ("https://regs.maryland.gov/us/md/exec/comar/07.03.21.04",)
    documentation = "Uses existing net business income without an additional expense deduction. MEAP depreciation add-backs are unsupported. Flooring losses is a modeling convention because the sources do not specify their treatment."

    def formula(person, period, parameters):
        p = parameters(period).gov.states.md.dhs.meap.income
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        counted = (person("age", period) >= p.earned_income_min_age) & ~person(
            "is_full_time_student", period
        )
        return where(counted, earned, 0)
