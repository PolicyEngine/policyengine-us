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
        simulation = person.simulation
        name = "slcsp_age_curve_amount_person"
        if hasattr(simulation, "_get_set_input_periods"):
            supplied = period in simulation._get_set_input_periods(name)
        else:
            # Older Core releases expose the constructor inputs and later
            # set_input provenance separately.
            branches = (
                simulation._get_visible_branch_names()
                if hasattr(simulation, "_get_visible_branch_names")
                else {getattr(simulation, "branch_name", "default"), "default"}
            )
            supplied = name in simulation.input_variables or any(
                variable == name and branch in branches and set_period == period
                for variable, branch, set_period in (
                    getattr(simulation, "_user_input_keys", None) or ()
                )
            )
        if supplied:
            return person(name, period)
        amount = person("slcsp_age_curve_amount_person", period)
        pays_premium = person("pays_aca_premium", period.this_year)
        base = person.household("slcsp_age_0", period)
        multiplier = person("slcsp_age_curve_multiplier", period)
        age_curve_applies = person.tax_unit("slcsp_age_curve_applies", period)
        return where(pays_premium, amount, base * multiplier * age_curve_applies)
