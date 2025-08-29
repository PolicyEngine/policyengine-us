from policyengine_us.model_api import *


class me_property_tax_fairness_credit_veterans_cap(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Veterans cap for Maine property tax fairness credit"
    definition_period = YEAR
    defined_for = StateCode.ME
    reference = {
        "title": "2024 SCHEDULE PTFC/STFC Form 1040ME",
        "href": "https://www.maine.gov/revenue/sites/maine.gov.revenue/files/inline-files/24_Form%201040ME_Sch%20PTFC_ff_0.pdf#page=2",
    }
    # Only one spouse needs to be a veteran for the filer to get the veteran match

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.me.tax.income.credits.fairness.property_tax
        base_cap = tax_unit("me_property_tax_fairness_credit_base_cap", period)
        # Check if the tax unit head or spouse is a veteran
        person = tax_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_veteran = person("is_veteran", period)
        has_veteran_head_or_spouse = tax_unit.any(
            is_head_or_spouse & is_veteran
        )
        return has_veteran_head_or_spouse * base_cap * p.veterans_matched
