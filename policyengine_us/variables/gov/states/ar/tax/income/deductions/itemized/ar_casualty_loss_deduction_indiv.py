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
        # 2025 Form AR3, Lines 18 and 30-35, and instructions for Lines 31-35
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR3_ItemizedDeduction.pdf#page=1",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2025_AR1000F_and_AR1000NR_Instructions.pdf#page=22",
    )
    defined_for = StateCode.AR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ar.tax.income.deductions.itemized.casualty_loss
        # A couple filing separately on the same return (status 4) files one
        # Form AR3 with one set of Forms AR4684, one form per casualty event.
        # AR4684 line 11 subtracts $100 once per event, whichever spouse owns
        # the property, and lines 13-18 apply one 10% floor for the return.
        # Line 17 cites AR1000F line 25 without naming a column; we use
        # columns A plus B, as AR3 lines 2 and 23 do for the other AGI
        # floors. AR3 lines 31-35 then split the whole itemized total, line
        # 18 included, by AGI share (ar_itemized_deductions_indiv), not by
        # who owned the property. The adopted 26 U.S.C. § 165(h)(5)(B) (2008
        # edition) treats only spouses on a joint return as one individual,
        # and Treas. Reg. § 1.165-7(b)(4)(iii) applies the $100 to each
        # spouse otherwise, but no Arkansas form or instruction computes the
        # loss per spouse, so we follow the forms. The model records one loss
        # amount per person, not separate casualty events, so the tax unit's
        # losses are treated as one casualty and the exclusion applies once.
        # A dependent's loss belongs on the dependent's own return under
        # § 165(h) as adopted by § 26-51-424(b), even though ar_agi_indiv
        # moves the dependent's net income to the head.
        loss = tax_unit_non_dep_add(tax_unit, period, ["casualty_loss"])
        loss_after_exclusion = max_(0, loss - p.exclusion)
        agi = add(tax_unit, period, ["ar_agi_indiv"])
        return max_(0, loss_after_exclusion - p.income_floor * agi)
