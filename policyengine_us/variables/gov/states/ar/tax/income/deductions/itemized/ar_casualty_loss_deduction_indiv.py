from policyengine_us.model_api import *


class ar_casualty_loss_deduction_indiv(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas casualty and theft loss deduction when married filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        # Ark. Code § 26-51-424(b), as amended by Act 372 of 2009, § 17
        "https://www.arkleg.state.ar.us/Acts/FTPDocument?path=%2FACTS%2F2009R%2FPublic%2F&file=372.pdf&ddBienniumSession=2009%2F2009R#page=5",
        "https://www.govinfo.gov/content/pkg/USCODE-2008-title26/html/USCODE-2008-title26-subtitleA-chap1-subchapB-partVI-sec165.htm",
        # 2025 Form AR3 instructions, Line 18, and Form AR4684
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=21",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR4684_Casualties_and_Thefts.pdf#page=1",
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ar.tax.income.deductions.itemized.casualty_loss
        # The model records one loss amount per person, not separate
        # casualty events, so the tax unit's losses are treated as one
        # casualty and the per-loss exclusion applies once.
        loss = add(tax_unit, period, ["casualty_loss"])
        loss_after_exclusion = max_(0, loss - p.exclusion)
        agi = add(tax_unit, period, ["ar_agi_indiv"])
        return max_(0, loss_after_exclusion - p.income_floor * agi)
