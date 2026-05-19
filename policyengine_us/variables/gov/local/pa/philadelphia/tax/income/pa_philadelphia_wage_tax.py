from policyengine_us.model_api import *


class pa_philadelphia_wage_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Philadelphia wage tax"
    documentation = (
        "Philadelphia employee wage or earnings tax based on explicit taxable "
        "wages and resident-status inputs."
    )
    definition_period = YEAR
    unit = USD
    reference = (
        "https://www.phila.gov/services/payments-assistance-taxes/taxes/"
        "business-taxes/business-taxes-by-type/wage-tax-employers/"
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        taxable_wages = person("pa_philadelphia_wage_tax_taxable_wages", period)
        if not np.any(taxable_wages):
            return 0

        p = parameters(period).gov.local.pa.philadelphia.tax.income
        resident = person("pa_philadelphia_wage_tax_resident", period)
        reduced_rate_eligible = person(
            "pa_philadelphia_wage_tax_reduced_rate_eligible", period
        )
        standard_rate = where(resident, p.resident_rate, p.nonresident_rate)
        rate = where(reduced_rate_eligible, p.reduced_rate, standard_rate)
        return tax_unit.sum(taxable_wages * rate)
