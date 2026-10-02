from policyengine_us.model_api import *


class ny_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York AGI subtractions"
    unit = USD
    documentation = "Subtractions from NY AGI over federal AGI."
    definition_period = YEAR
    reference = (
        # N.Y. Tax Law § 612(a), (c)(3), (c)(3-a), (c)(3-c), (c)(7)
        "https://newyork.public.law/laws/n.y._tax_law_section_612",
        # 2025 Form IT-201-I, who must file (dependents)
        "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=3",
        # 2025 Form IT-201-I, lines 26 and 29
        "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=9",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.agi.subtractions
        # Each subtraction applies only to amounts included in federal AGI.
        # Dependents' income is not in the filer's federal AGI; they report
        # it on their own return, so only the head's and spouse's count.
        total_subtractions = tax_unit_non_dep_add(tax_unit, period, p.sources)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
