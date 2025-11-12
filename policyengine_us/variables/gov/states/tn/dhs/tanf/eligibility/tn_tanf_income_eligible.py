from policyengine_us.model_api import *


class tn_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Tennessee TANF income eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/tennessee/Tenn-Comp-R-Regs-1240-01-50-.20",
        "Tennessee Administrative Code § 1240-01-50-.20 - Standard of Need/Income",
        "Tennessee TANF State Plan 2024-2027",
    )
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        # Calculate gross income for initial test using federal TANF variables
        person = spm_unit.members
        gross_earned = spm_unit.sum(person("tanf_gross_earned_income", period))
        gross_unearned = spm_unit.sum(
            person("tanf_gross_unearned_income", period)
        )
        gross_income = gross_earned + gross_unearned

        # Determine unit size
        p = parameters(period).gov.states.tn.dhs.tanf
        unit_size = spm_unit.nb_persons()
        max_size = p.eligibility.max_family_size
        capped_size = min_(unit_size, max_size)

        # Get Consolidated Need Standard (CNS) for family size
        cns = p.benefit.consolidated_need_standard[capped_size]

        # Calculate Gross Income Standard (GIS) = 185% of CNS
        # Per Tenn. Comp. R. & Regs. 1240-01-50-.20:
        # "This standard is set at One Hundred Eighty-Five Percent (185%)
        # of the consolidated need standard."
        gis_percentage = p.income.gis_percentage
        gis = cns * gis_percentage
        gross_income_test = gross_income <= gis

        # Check net income test (countable income < CNS)
        countable_income = spm_unit("tn_tanf_countable_income", period)
        net_income_test = countable_income < cns

        # Must pass both tests
        return gross_income_test & net_income_test
