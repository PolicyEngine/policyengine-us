from policyengine_us.model_api import *


class nm_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/1afc56af-ea90-4d48-82e5-1f9aeb43255a/PITbook2022.pdf",
        # NMSA 1978 7-2-2(N)(2): itemized deductions allowed under the IRC.
        "https://www.nmlegis.gov/Sessions/23%20Regular/final/HB0368.pdf#page=7",
        "https://realfile.tax.newmexico.gov/2025pit-1-ins.pdf#page=25",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.limitation
        if p.obbb.applies:
            # From 2026 the allowed federal total is net of section 68.
            return tax_unit("itemized_taxable_income_deductions", period)
        return tax_unit("total_itemized_taxable_income_deductions", period)
