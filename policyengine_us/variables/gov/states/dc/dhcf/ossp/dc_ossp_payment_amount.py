from policyengine_us.model_api import *


class dc_ossp_payment_amount(Variable):
    value_type = float
    entity = Person
    label = "DC OSSP monthly payment amount"
    unit = USD
    definition_period = MONTH
    defined_for = "dc_ossp_eligible"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/4-205.49",
        "https://secure.ssa.gov/apps10/poms.nsf/lnx/0501415058#d",
    )

    def formula(person, period, parameters):
        living_arrangement = person("dc_ossp_living_arrangement", period)
        eligible = person("dc_ossp_eligible", period)
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        both_eligible = person.marital_unit.sum(eligible) == 2
        # Couple rate requires joint SSI claim, both spouses OSSP-eligible,
        # and both in the same arrangement category.
        is_os_a = living_arrangement == living_arrangement.possible_values.OS_A
        is_os_b = living_arrangement == living_arrangement.possible_values.OS_B
        is_os_g = living_arrangement == living_arrangement.possible_values.OS_G
        both_same = (
            (person.marital_unit.sum(is_os_a) == 2)
            | (person.marital_unit.sum(is_os_b) == 2)
            | (person.marital_unit.sum(is_os_g) == 2)
        )
        is_couple = joint_claim & both_eligible & both_same
        p = parameters(period).gov.states.dc.dhcf.ossp.payment

        return where(
            is_couple,
            p.couple[living_arrangement] / 2,
            p.individual[living_arrangement],
        )
