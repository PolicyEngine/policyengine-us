from policyengine_us.model_api import *


class marketplace_csr_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Tax unit is eligible for ordinary Marketplace cost-sharing reductions"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/45/155.305#g"
    documentation = (
        "The model prices one Marketplace policy per tax unit. Under 45 CFR "
        "155.305(g)(3), a policy covering people who would be eligible for "
        "different cost-sharing reductions gets only the category all of "
        "them qualify for, so a policy that also covers an enrollee without "
        "premium tax credit eligibility (one outside the tax family, such as "
        "a spouse who can be claimed on another return) gets none."
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        receives_aca = tax_unit.sum(person("person_receives_aca", period)) > 0
        enrollee = person("pays_aca_premium", period)
        ptc_eligible = person("is_aca_ptc_eligible", period)
        every_enrollee_eligible = ~tax_unit.any(enrollee & ~ptc_eligible)
        category = tax_unit("selected_marketplace_plan_category", period)
        silver_selected = category == category.possible_values.SILVER
        magi_fraction = tax_unit("aca_magi_fraction", period)
        income_eligible = (
            magi_fraction <= parameters(period).gov.aca.csr.income_threshold.maximum
        )
        return (
            receives_aca & every_enrollee_eligible & silver_selected & income_eligible
        )
