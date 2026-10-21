from policyengine_us.model_api import *


class nc_mortgage_and_property_tax_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina mortgage interest and real estate property tax deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Form D-400 Schedule A line 5: the smaller of the amount before limitation (line 3) and the limitation (line 4)."
    reference = (
        # N.C. Gen. Stat. 105-153.5(a)(2)b
        "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-153.5.html",
        # 2025 Form D-401 instructions, Form D-400 Schedule A line 5
        "https://www.ncdor.gov/2025-d-401-individual-income-tax-instructions/open#page=20",
    )
    defined_for = StateCode.NC

    def formula(tax_unit, period, parameters):
        before_limitation = tax_unit(
            "nc_mortgage_and_property_tax_before_limitation", period
        )
        limitation = tax_unit("nc_mortgage_and_property_tax_limitation", period)
        return min_(before_limitation, limitation)
