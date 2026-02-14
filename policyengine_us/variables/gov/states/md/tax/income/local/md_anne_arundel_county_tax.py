from policyengine_us.model_api import *


class md_anne_arundel_county_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Anne Arundel County local income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=25"

    def formula(tax_unit, period, parameters):
        county = tax_unit.household("county_str", period)
        is_anne_arundel = county == "ANNE_ARUNDEL_COUNTY_MD"

        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        taxable_income = tax_unit("md_taxable_income", period)

        p = parameters(period).gov.local.md.anne_arundel_county.tax.income

        # Filing status conditions
        is_single = filing_status == filing_statuses.SINGLE
        is_joint = filing_status == filing_statuses.JOINT
        is_separate = filing_status == filing_statuses.SEPARATE
        is_head_of_household = (
            filing_status == filing_statuses.HEAD_OF_HOUSEHOLD
        )
        is_surviving_spouse = filing_status == filing_statuses.SURVIVING_SPOUSE

        # Tax calculations for each filing status
        single_tax = p.single.calc(taxable_income)
        joint_tax = p.joint.calc(taxable_income)
        separate_tax = p.separate.calc(taxable_income)
        head_of_household_tax = p.head_of_household.calc(taxable_income)
        surviving_spouse_tax = p.surviving_spouse.calc(taxable_income)

        # Select tax based on filing status
        tax = select(
            [
                is_single,
                is_joint,
                is_separate,
                is_head_of_household,
                is_surviving_spouse,
            ],
            [
                single_tax,
                joint_tax,
                separate_tax,
                head_of_household_tax,
                surviving_spouse_tax,
            ],
        )

        return where(is_anne_arundel, tax, 0)
