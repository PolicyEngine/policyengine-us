from policyengine_us.model_api import *


class co_leap_countable_income_person(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Colorado LEAP countable person income"
    defined_for = StateCode.CO
    # PDF pages 46-48,51
    reference = (
        "https://drive.google.com/file/d/1G3XKsXyKoPZmsA5-P6NI6w3svP99xOZd/view#page=46"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.co.cdhs.leap.income
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        age = person("age", period)
        earned = where(age >= p.earned_min_age, earned, 0)
        unearned = sum(max_(person(source, period), 0) for source in p.sources.unearned)
        # Annual flows approximate ongoing application-month income. The
        # monthly SSA and SSI amounts lose cents separately for each person.
        # Medicare premiums remain in gross SSA income under Colorado rules.
        social_security = np.floor(person("social_security", period) / MONTHS_IN_YEAR)
        ssi = np.floor(person("ssi", period, options=[ADD]) / MONTHS_IN_YEAR)
        income = earned + unearned + (social_security + ssi) * MONTHS_IN_YEAR
        foster = person("is_in_foster_care", period.first_month)
        # Known foster individuals are outside the LEAP household; income of
        # nonqualified immigrants remains included. Each received income source
        # is nonnegative, and existing business inputs are already net of costs.
        return where(foster, 0, max_(income, 0))
