from policyengine_us.model_api import *


class md_local_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD local income tax before credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        county = tax_unit.household("county_str", period)
        in_md = tax_unit.household("state_code_str", period) == "MD"
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        taxable_income = tax_unit("md_taxable_income", period)
        p_local = parameters(period).gov.local.md
        county_rates = p_local.all_other_counties.flat_rate

        # Counties with progressive structures
        anne_arundel = county == "ANNE_ARUNDEL_COUNTY_MD"
        frederick = county == "FREDERICK_COUNTY_MD"

        # Anne Arundel County progressive tax
        aa = p_local.anne_arundel_county.tax.income
        anne_arundel_tax = where(
            anne_arundel,
            select(
                [
                    filing_status == filing_statuses.SINGLE,
                    filing_status == filing_statuses.JOINT,
                    filing_status == filing_statuses.SEPARATE,
                    filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                    filing_status == filing_statuses.SURVIVING_SPOUSE,
                ],
                [
                    aa.single.calc(taxable_income),
                    aa.joint.calc(taxable_income),
                    aa.separate.calc(taxable_income),
                    aa.head_of_household.calc(taxable_income),
                    aa.surviving_spouse.calc(taxable_income),
                ],
            ),
            0,
        )

        # Frederick County progressive tax
        fc = p_local.frederick_county.tax.income
        frederick_tax = where(
            frederick,
            select(
                [
                    filing_status == filing_statuses.SINGLE,
                    filing_status == filing_statuses.JOINT,
                    filing_status == filing_statuses.SEPARATE,
                    filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                    filing_status == filing_statuses.SURVIVING_SPOUSE,
                ],
                [
                    fc.single.calc(taxable_income),
                    fc.joint.calc(taxable_income),
                    fc.separate.calc(taxable_income),
                    fc.head_of_household.calc(taxable_income),
                    fc.surviving_spouse.calc(taxable_income),
                ],
            ),
            0,
        )

        # Flat rate counties - use breakdown parameter lookup
        flat_rate = county_rates[county]
        flat_rate_tax = flat_rate * taxable_income

        # Progressive counties should not use flat rate
        is_progressive_county = anne_arundel | frederick
        flat_rate_tax = where(is_progressive_county, 0, flat_rate_tax)

        # Sum progressive and flat rate taxes
        total_tax = anne_arundel_tax + frederick_tax + flat_rate_tax

        return where(in_md, total_tax, 0)
