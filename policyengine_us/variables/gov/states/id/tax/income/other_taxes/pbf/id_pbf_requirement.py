from policyengine_us.model_api import *


class id_pbf_requirement(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Idaho PBF tax exemption credit"
    definition_period = YEAR
    reference = "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_11-15-2021.pdf#page=10"
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        spm_unit = tax_unit.spm_unit
        p = parameters(period).gov.states.id.tax.income.other_taxes.pbf

        # eligible if income less than filing status specified amount
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        # joint_status = filing_status.possible_values.JOINT
        # widow_status = filing_status.possible_values.WIDOW
        # dependent_count = tax_unit("tax_unit_dependents", period)

        elder_head = tax_unit("age_head", period) >= p.age_threshold
        elder_spouse = tax_unit("age_spouse", period) >= p.age_threshold
        income_ineligible_check = where(
            elder_head | elder_spouse,
            income
            < p.income_threshold.older.threshold_partial_65_and_above[
                filing_status
            ],
            income
            < p.income_threshold.younger.threshold_under_65[filing_status],
        )
        income_ineligible = where(
            elder_head & elder_spouse,
            income
            < p.income_threshold.older.threshold_65_and_above[filing_status],
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
