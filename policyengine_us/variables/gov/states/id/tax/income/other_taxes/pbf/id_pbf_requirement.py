from policyengine_us.model_api import *


class id_pbf_requirement(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Required to pay the Idaho permanent building fund tax"
    definition_period = YEAR
    reference = "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_11-15-2021.pdf#page=10"
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        spm_unit = tax_unit.spm_unit
        p = parameters(period).gov.states.id.tax.income.other_taxes.pbf

        # eligible if income less than filing status specified amount
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)

        elder_head = tax_unit("age_head", period) >= p.age_threshold
        elder_spouse = tax_unit("age_spouse", period) >= p.age_threshold

        # income check for three age conditions
        income_ineligible_older_two_aged = (
            income < p.income_threshold.older.two_aged[filing_status]
        )
        income_ineligible_older_one_aged = (
            income < p.income_threshold.older.one_aged[filing_status]
        )
        income_ineligible_younger = (
            income < p.income_threshold.younger[filing_status]
        )

        income_ineligible_check = where(
            elder_head | elder_spouse,
            income_ineligible_older_one_aged,
            income_ineligible_younger,
        )
        income_ineligible = where(
            elder_head & elder_spouse,
            income_ineligible_older_two_aged,
            income_ineligible_check,
        )

        # eligible if receiving public assistance tanf
        tanf_received = spm_unit("tanf", period)
        tanf_ineligible = tanf_received > 0

        # eligible if head or spouse is blind
        blind_head = tax_unit("blind_head", period)
        blind_spouse = tax_unit("blind_spouse", period)
        blind_ineligible = blind_head | blind_spouse

        return ~income_ineligible & ~tanf_ineligible & ~blind_ineligible
