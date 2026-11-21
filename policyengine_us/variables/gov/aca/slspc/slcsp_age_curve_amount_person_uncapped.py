from policyengine_us.model_api import *


class slcsp_age_curve_amount_person_uncapped(Variable):
    value_type = float
    entity = Person
    label = "Second-lowest ACA silver-plan cost before the three-child premium cap"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/cfr/text/45/147.102#c_1"
    documentation = (
        "The person's age-rated benchmark before limiting a family's charges "
        "to its three oldest covered children. For premium payers, read "
        "slcsp_age_curve_amount_person directly. Supplied premiums, including "
        "zero, carry through regardless of premium-payment status. A child "
        "who adds no premium to the whole policy may add "
        "one when a different coverage family is priced, so derive that "
        "person's uncapped quote separately."
    )

    def formula(person, period, parameters):
        name = "slcsp_age_curve_amount_person"
        if has_input_for_period(person.simulation, name, period):
            return person(name, period)
        amount = person("slcsp_age_curve_amount_person", period)
        pays_premium = person("pays_aca_premium", period.this_year)
        base = person.household("slcsp_age_0", period)
        multiplier = person("slcsp_age_curve_multiplier", period)
        age_curve_applies = person.tax_unit("slcsp_age_curve_applies", period)
        return where(pays_premium, amount, base * multiplier * age_curve_applies)
