from policyengine_us.model_api import *


class md_frederick_county_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Frederick County local income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=25"

    def formula(tax_unit, period, parameters):
        county = tax_unit.household("county_str", period)
        is_frederick = county == "FREDERICK_COUNTY_MD"

        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        taxable_income = tax_unit("md_taxable_income", period)

        p = parameters(period).gov.local.md.frederick_county.tax.income

        # Filing status conditions
        is_single = filing_status == filing_statuses.SINGLE
        is_joint = filing_status == filing_statuses.JOINT
        is_separate = filing_status == filing_statuses.SEPARATE
        is_head_of_household = (
            filing_status == filing_statuses.HEAD_OF_HOUSEHOLD
        )
        is_surviving_spouse = filing_status == filing_statuses.SURVIVING_SPOUSE

        # Frederick County uses fixed-rate-by-bracket (NOT marginal rates)
        # The entire income is multiplied by the single rate for the bracket
        single_rate = p.single.calc(taxable_income, right=True)
        joint_rate = p.joint.calc(taxable_income, right=True)
        separate_rate = p.separate.calc(taxable_income, right=True)
        head_of_household_rate = p.head_of_household.calc(
            taxable_income, right=True
        )
        surviving_spouse_rate = p.surviving_spouse.calc(
            taxable_income, right=True
        )

        # Select rate based on filing status
        rate = select(
            [
                is_single,
                is_joint,
                is_separate,
                is_head_of_household,
                is_surviving_spouse,
            ],
            [
                single_rate,
                joint_rate,
                separate_rate,
                head_of_household_rate,
                surviving_spouse_rate,
            ],
        )

        # Fixed rate: entire income * bracket rate
        tax = taxable_income * rate

        return where(is_frederick, tax, 0)
