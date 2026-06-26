from policyengine_us.model_api import *


class ky_fayette_occupational_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Lexington/Fayette County occupational license tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    reference = "https://www.lexingtonky.gov/departments/revenue"

    def formula(tax_unit, period, parameters):
        # Lexington is consolidated with Fayette County (LFUCG), so it is
        # assigned via county. The occupational license fee is workplace-based;
        # modeled here as residence-based (work locality = residence locality).
        county = tax_unit.household("county_str", period)
        in_fayette = county == "FAYETTE_COUNTY_KY"
        rate = parameters(period).gov.local.ky.fayette.tax.income.occupational.rate
        person = tax_unit.members
        earnings = max_(
            person("employment_income", period)
            + person("self_employment_income", period),
            0,
        )
        return where(in_fayette, tax_unit.sum(earnings), 0) * rate
