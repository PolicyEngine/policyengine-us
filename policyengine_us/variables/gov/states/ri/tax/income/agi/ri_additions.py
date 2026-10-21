from policyengine_us.model_api import *


class ri_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island AGI Additions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%20RI%20Schedule%20M_w.pdf#page=2",
        # R.I. Gen. Laws § 44-30-12(a) and (b)(6)
        "https://webserver.rilegislature.gov/Statutes/TITLE44/44-30/44-II/44-30-12.htm",
        # 2020 RI Schedule M line 2g
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/forms/2020/Income/2020-RI-Schedule-M_w.pdf#page=2",
        # PDF pages 1, 9: who must file; Schedule M line 2g
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/forms/2020/Income/2020-Resident-Instructions_03282021.pdf#page=1",
    )
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.agi.additions
        # The additions modify the filers' federal AGI. A tax unit
        # dependent's income, including their federally excluded
        # unemployment compensation, is on their own return, so person-level
        # additions count only the head and spouse.
        return tax_unit_non_dep_add(tax_unit, period, p.additions)
