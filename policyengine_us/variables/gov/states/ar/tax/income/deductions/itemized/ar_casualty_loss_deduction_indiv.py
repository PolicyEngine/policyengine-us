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
        # Incorporated IRC § 165(h)(1)-(2) and (5)(B), 2011 edition
        "https://www.govinfo.gov/content/pkg/USCODE-2011-title26/pdf/USCODE-2011-title26-subtitleA-chap1-subchapB-partVI-sec165.pdf#page=1",
        "https://www.govinfo.gov/content/pkg/USCODE-2011-title26/pdf/USCODE-2011-title26-subtitleA-chap1-subchapB-partVI-sec165.pdf#page=2",
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
        # Incorporated IRC § 165(h)(1)-(2) applies the exclusion and AGI
        # floor to each separate filer; only joint-return spouses count as
        # one individual under § 165(h)(5)(B). The input records one
        # casualty event per person. AR3 subsequently prorates the total
        # itemized deductions by AGI in ar_itemized_deductions_indiv.
        loss = tax_unit.members("casualty_loss", period)
        loss_after_exclusion = max_(0, loss - p.exclusion)
        agi = max_(tax_unit.members("ar_agi_indiv", period), 0)
        deduction = max_(0, loss_after_exclusion - p.income_floor * agi)
        non_dependent = not_(tax_unit.members("is_tax_unit_dependent", period))
        return tax_unit.sum(deduction * non_dependent)
