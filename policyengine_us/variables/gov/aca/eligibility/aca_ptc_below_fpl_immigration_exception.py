from policyengine_us.model_api import *


class aca_ptc_below_fpl_immigration_exception(Variable):
    value_type = bool
    entity = TaxUnit
    label = "ACA PTC below-FPL immigration exception"
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/36B#c_1_B",
        "https://www.law.cornell.edu/cfr/text/26/1.36B-2#b_5",
    ]

    def formula(tax_unit, period, parameters):
        in_effect = parameters(period).gov.aca.below_fpl_immigration_exception_in_effect
        below_fpl = tax_unit("aca_magi_fraction", period) < 1

        person = tax_unit.members
        immigration_status = person("immigration_status", period)
        non_citizen = immigration_status != immigration_status.possible_values.CITIZEN
        aca_lawfully_present = person("is_aca_ptc_immigration_status_eligible", period)
        medicaid_ineligible_due_to_status = ~person(
            "is_medicaid_immigration_status_eligible", period
        )

        qualifying_family_member = tax_unit.any(
            non_citizen & aca_lawfully_present & medicaid_ineligible_due_to_status
        )
        return in_effect & below_fpl & qualifying_family_member
