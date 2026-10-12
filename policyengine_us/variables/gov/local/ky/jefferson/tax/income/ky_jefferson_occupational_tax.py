from policyengine_us.model_api import *


class ky_jefferson_occupational_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisville/Jefferson County occupational license tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    reference = "https://louisvilleky.gov/sites/default/files/2024-12/w-1kjc_instructions_2025.pdf"

    def formula(tax_unit, period, parameters):
        # Louisville Metro is consolidated with Jefferson County, so it is
        # assigned via county. The occupational license fee is workplace-based;
        # modeled here as residence-based (work locality = residence locality).
        county = tax_unit.household("county_str", period)
        in_jefferson = county == "JEFFERSON_COUNTY_KY"
        rate = parameters(period).gov.local.ky.jefferson.tax.income.occupational.rate
        person = tax_unit.members
        earnings = max_(
            person("employment_income", period)
            + person("self_employment_income", period),
            0,
        )
        return where(in_jefferson, tax_unit.sum(earnings), 0) * rate
