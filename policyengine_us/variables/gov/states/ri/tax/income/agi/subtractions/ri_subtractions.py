from policyengine_us.model_api import *


class ri_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island AGI Subtractions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%201041%20Schedule%20M_w.pdf#page=1",
        # R.I. Gen. Laws § 44-30-12(a) and (c)(11)
        "https://webserver.rilegislature.gov/Statutes/TITLE44/44-30/44-II/44-30-12.htm",
        # Who must file (page I-1); RI Schedule M line 1v (page I-10)
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2025-12/2025%201040R%20Instructions%20122025.pdf#page=1",
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2025-12/2025%201040R%20Instructions%20122025.pdf#page=10",
    )
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.agi.subtractions
        # Dependents' income is not in federal AGI; they report it on their
        # own return, so person-level subtractions count only the head and
        # spouse.
        total_subtractions = tax_unit_non_dep_add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
