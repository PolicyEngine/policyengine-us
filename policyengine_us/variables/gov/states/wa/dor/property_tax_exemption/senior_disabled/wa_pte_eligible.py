from policyengine_us.model_api import *


class wa_pte_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Washington Senior Citizens and Disabled Persons Property Tax Exemption"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.381",
        "https://dor.wa.gov/sites/default/files/2022-02/PTExemption_Senior.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        # RCW 84.36.381(2) requires the person claiming the exemption to own
        # the residence. The qualifying filer must be the head or, if the
        # return is joint, the spouse. `is_tax_unit_spouse` alone classifies
        # the highest-age non-head adult as "spouse" even outside marriage,
        # so it is paired with `tax_unit_is_joint` to avoid awarding the
        # exemption when only a dependent is categorically eligible.
        person = tax_unit.members
        categorical = person("wa_pte_categorical_eligible", period)
        head = person("is_tax_unit_head", period)
        is_joint = person.tax_unit("tax_unit_is_joint", period)
        spouse_in_joint = person("is_tax_unit_spouse", period) & is_joint
        qualifying_filer = head | spouse_in_joint
        has_qualifying_filer = tax_unit.any(categorical & qualifying_filer)
        # Owner-occupancy proxy: only homeowners pay real_estate_taxes directly.
        pays_property_tax = add(tax_unit, period, ["real_estate_taxes"]) > 0
        income_eligible = tax_unit("wa_pte_income_eligible", period)
        return has_qualifying_filer & pays_property_tax & income_eligible
