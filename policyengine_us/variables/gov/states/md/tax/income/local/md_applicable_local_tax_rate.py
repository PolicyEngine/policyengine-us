from policyengine_us.model_api import *


class md_applicable_local_tax_rate(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD applicable local income tax rate"
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-704&enactments=false",
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=26",
    )

    def formula(tax_unit, period, parameters):
        county = tax_unit.household("county_str", period)

        # Guard against non-MD counties in microsimulation:
        # defined_for masks results but doesn't prevent formula execution.
        in_md = tax_unit.household("state_code_str", period) == "MD"
        safe_county = where(in_md, county, "ALLEGANY_COUNTY_MD")

        p = parameters(period).gov.local.md
        flat_rate = p.flat_rate[safe_county]

        # Anne Arundel County imposes its tax on a marginal-rate basis, so
        # § 10-704(d)(2) applies its lowest marginal rate.
        is_anne_arundel = county == "ANNE_ARUNDEL_COUNTY_MD"
        anne_arundel_rate = p.anne_arundel_county.tax.income.single.rates[0]

        # Frederick County applies a fixed rate by bracket, so the rate
        # applicable to the taxpayer's income level and filing status
        # applies.
        is_frederick = county == "FREDERICK_COUNTY_MD"
        frederick_rate = tax_unit("md_frederick_county_tax_rate", period)

        rate = select(
            [is_anne_arundel, is_frederick],
            [anne_arundel_rate, frederick_rate],
            default=flat_rate,
        )
        return rate * in_md
