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
        p = parameters(period).gov.local.md.maryland_counties

        # Counties with progressive structures
        anne_arundel = county == "ANNE_ARUNDEL_COUNTY_MD"
        frederick = county == "FREDERICK_COUNTY_MD"

        # Anne Arundel County progressive tax
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
                    p.anne_arundel_county.tax.income.single.calc(
                        taxable_income
                    ),
                    p.anne_arundel_county.tax.income.joint.calc(
                        taxable_income
                    ),
                    p.anne_arundel_county.tax.income.separate.calc(
                        taxable_income
                    ),
                    p.anne_arundel_county.tax.income.head_of_household.calc(
                        taxable_income
                    ),
                    p.anne_arundel_county.tax.income.surviving_spouse.calc(
                        taxable_income
                    ),
                ],
            ),
            0,
        )

        # Frederick County progressive tax
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
                    p.frederick_county.tax.income.single.calc(taxable_income),
                    p.frederick_county.tax.income.joint.calc(taxable_income),
                    p.frederick_county.tax.income.separate.calc(
                        taxable_income
                    ),
                    p.frederick_county.tax.income.head_of_household.calc(
                        taxable_income
                    ),
                    p.frederick_county.tax.income.surviving_spouse.calc(
                        taxable_income
                    ),
                ],
            ),
            0,
        )

        # Flat rate counties
        allegany = where(
            county == "ALLEGANY_COUNTY_MD",
            p.allegany_county.tax.income.rate * taxable_income,
            0,
        )
        baltimore_city = where(
            county == "BALTIMORE_CITY_MD",
            p.baltimore_city.tax.income.rate * taxable_income,
            0,
        )
        baltimore_county = where(
            county == "BALTIMORE_COUNTY_MD",
            p.baltimore_county.tax.income.rate * taxable_income,
            0,
        )
        calvert = where(
            county == "CALVERT_COUNTY_MD",
            p.calvert_county.tax.income.rate * taxable_income,
            0,
        )
        caroline = where(
            county == "CAROLINE_COUNTY_MD",
            p.caroline_county.tax.income.rate * taxable_income,
            0,
        )
        carroll = where(
            county == "CARROLL_COUNTY_MD",
            p.carroll_county.tax.income.rate * taxable_income,
            0,
        )
        cecil = where(
            county == "CECIL_COUNTY_MD",
            p.cecil_county.tax.income.rate * taxable_income,
            0,
        )
        charles = where(
            county == "CHARLES_COUNTY_MD",
            p.charles_county.tax.income.rate * taxable_income,
            0,
        )
        dorchester = where(
            county == "DORCHESTER_COUNTY_MD",
            p.dorchester_county.tax.income.rate * taxable_income,
            0,
        )
        garrett = where(
            county == "GARRETT_COUNTY_MD",
            p.garrett_county.tax.income.rate * taxable_income,
            0,
        )
        harford = where(
            county == "HARFORD_COUNTY_MD",
            p.harford_county.tax.income.rate * taxable_income,
            0,
        )
        howard = where(
            county == "HOWARD_COUNTY_MD",
            p.howard_county.tax.income.rate * taxable_income,
            0,
        )
        kent = where(
            county == "KENT_COUNTY_MD",
            p.kent_county.tax.income.rate * taxable_income,
            0,
        )
        montgomery = where(
            county == "MONTGOMERY_COUNTY_MD",
            p.montgomery_county.tax.income.rate * taxable_income,
            0,
        )
        prince_georges = where(
            county == "PRINCE_GEORGE_S_COUNTY_MD",
            p.prince_georges_county.tax.income.rate * taxable_income,
            0,
        )
        queen_annes = where(
            county == "QUEEN_ANNE_S_COUNTY_MD",
            p.queen_annes_county.tax.income.rate * taxable_income,
            0,
        )
        somerset = where(
            county == "SOMERSET_COUNTY_MD",
            p.somerset_county.tax.income.rate * taxable_income,
            0,
        )
        st_marys = where(
            county == "ST_MARY_S_COUNTY_MD",
            p.st_marys_county.tax.income.rate * taxable_income,
            0,
        )
        talbot = where(
            county == "TALBOT_COUNTY_MD",
            p.talbot_county.tax.income.rate * taxable_income,
            0,
        )
        washington = where(
            county == "WASHINGTON_COUNTY_MD",
            p.washington_county.tax.income.rate * taxable_income,
            0,
        )
        wicomico = where(
            county == "WICOMICO_COUNTY_MD",
            p.wicomico_county.tax.income.rate * taxable_income,
            0,
        )
        worcester = where(
            county == "WORCESTER_COUNTY_MD",
            p.worcester_county.tax.income.rate * taxable_income,
            0,
        )

        # Sum all county taxes (only one will be non-zero per entity)
        total_tax = (
            anne_arundel_tax
            + frederick_tax
            + allegany
            + baltimore_city
            + baltimore_county
            + calvert
            + caroline
            + carroll
            + cecil
            + charles
            + dorchester
            + garrett
            + harford
            + howard
            + kent
            + montgomery
            + prince_georges
            + queen_annes
            + somerset
            + st_marys
            + talbot
            + washington
            + wicomico
            + worcester
        )

        return where(in_md, total_tax, 0)
