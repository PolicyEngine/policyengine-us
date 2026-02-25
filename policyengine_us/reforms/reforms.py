from .congress.delauro import create_american_family_act_with_baby_bonus_reform
from .dc_kccatc import create_dc_kccatc_reform
from .winship import create_eitc_winship_reform
from .dc_tax_threshold_joint_ratio import (
    create_dc_tax_threshold_joint_ratio_reform,
)
from .congress.romney.family_security_act import (
    create_remove_head_of_household_reform,
)
from .cbo.payroll import (
    create_increase_taxable_earnings_for_social_security_reform,
)
from .congress.wyden_smith import create_ctc_expansion_reform
from .federal import create_abolish_federal_income_tax_reform
from .federal import create_abolish_payroll_tax_reform
from .federal import create_reported_state_income_tax_reform
from .biden.budget_2025 import (
    create_medicare_and_investment_tax_increase_reform,
)
from .biden.budget_2025 import create_capital_gains_tax_increase_reform
from .eitc import create_halve_joint_eitc_phase_out_rate_reform
from .states.ny.wftc import create_ny_working_families_tax_credit_reform
from .states.ny.a04038 import create_ny_a04038_enhanced_escc_infants_reform
from .states.sc.h3492 import create_sc_h3492_eitc_refundable_reform
from .states.ny.a06774 import create_ny_a06774_enhanced_cdcc_reform
from .states.ny.s04487 import create_ny_s04487_newborn_credit_reform
from .harris.lift.middle_class_tax_credit import (
    create_middle_class_tax_credit_reform,
)
from .harris.rent_relief_act.rent_relief_tax_credit import (
    create_rent_relief_tax_credit_reform,
)
from .congress.tlaib import (
    create_end_child_poverty_act_reform,
)
from .congress.tlaib.economic_dignity_for_all_agenda import (
    create_end_child_poverty_act_reform as create_edaa_end_child_poverty_act_reform,
)
from .congress.tlaib.boost import (
    create_boost_middle_class_tax_credit_reform,
)
from .states.mn.walz import (
    create_mn_walz_hf1938_repeal_reform,
)
from .states.oregon.rebate import (
    create_or_rebate_state_tax_exempt_reform,
)
from .congress.romney.family_security_act_2024.ctc import (
    create_family_security_act_2024_ctc_reform,
)
from .congress.romney.family_security_act_2024.eitc import (
    create_family_security_act_2024_eitc_reform,
)
from .treasury.repeal_dependent_exemptions import (
    create_repeal_dependent_exemptions_reform,
)
from .harris.capital_gains import (
    create_harris_capital_gains_reform,
)
from .tax_exempt.tax_exempt_reform import (
    create_tax_exempt_reform,
)
from .state_dependent_exemptions import (
    create_repeal_state_dependent_exemptions_reform,
)
from .ctc import (
    create_ctc_older_child_supplement_reform,
    create_ctc_additional_bracket_reform,
    create_ctc_per_child_phase_in_reform,
    create_ctc_per_child_phase_out_reform,
    create_ctc_minimum_refundable_amount_reform,
)
from .snap import (
    create_abolish_snap_deductions_reform,
    create_abolish_snap_net_income_test_reform,
)
from .states.dc.property_tax import create_dc_property_tax_credit_reform

from .deductions.salt import (
    create_limit_salt_deduction_to_property_taxes_reform,
)

from .local.nyc.stc.phase_out import (
    create_nyc_school_tax_credit_with_phase_out_reform,
)

from .states.mt.ctc import (
    create_mt_ctc_reform,
)
from .congress.golden import (
    create_fisc_act_reform,
)
from .crfb import (
    create_tax_employer_social_security_tax_reform,
    create_tax_employer_medicare_tax_reform,
    create_tax_employer_payroll_tax_reform,
)
from .congress.afa import (
    create_afa_other_dependent_credit_reform,
)

from .reconciliation import (
    create_reconciled_ssn_for_llc_and_aoc_reform,
)
from .states.mi.surtax import (
    create_mi_surtax_reform,
)
from .local.ny.mamdani_income_tax import (
    create_nyc_mamdani_income_tax_reform,
)
from .states.ut import (
    create_ut_refundable_eitc_reform,
    create_ut_hb210_reform,
    create_ut_hb210_s2_reform,
)
from .additional_tax_bracket import (
    create_additional_tax_bracket_reform,
)
from .congress.hawley.awra import (
    create_american_worker_rebate_act_reform,
)
from .crfb import (
    create_non_refundable_ss_credit_reform,
    create_senior_deduction_extension_reform,
    create_agi_surtax_reform,
)
from .states.ri.ctc.ri_ctc_reform import create_ri_ctc_reform
from .states.ri.exemption.ri_exemption_reform import (
    create_ri_exemption_reform_fn,
)
from .states.de.dependent_credit.de_dependent_credit_reform import (
    create_de_dependent_credit_reform_fn,
)
from .states.oregon.dependent_exemption_credit.or_dependent_exemption_credit_reform import (
    create_or_dependent_exemption_credit_reform_fn,
)
from .states.va.dependent_exemption.va_dependent_exemption_reform import (
    create_va_dependent_exemption_reform_fn,
)
from .states.va.hb979.va_hb979_reform import (
    create_va_hb979_reform,
)
from .states.ct.refundable_ctc import (
    create_ct_refundable_ctc_reform,
)
from .aca import (
    create_aca_ptc_additional_bracket_reform,
    create_aca_ptc_simplified_bracket_reform,
    create_aca_ptc_700_fpl_cliff_reform,
)
from .cdcc import (
    create_cdcc_single_parent_work_requirement_reform,
)
from .states.ct.sb100 import (
    create_ct_sb100_reform,
)
from .states.ct.tax_rebate_2026 import (
    create_ct_tax_rebate_2026_reform,
)
from .states.ct.hb5009 import (
    create_ct_hb5009_reform,
)


from policyengine_core.reforms import Reform
import warnings


def create_structural_reforms_from_parameters(parameters, period):
    afa_reform = create_american_family_act_with_baby_bonus_reform(
        parameters, period
    )
    winship_reform = create_eitc_winship_reform(parameters, period)
    dc_kccatc_reform = create_dc_kccatc_reform(parameters, period)
    dc_tax_threshold_joint_ratio_reform = (
        create_dc_tax_threshold_joint_ratio_reform(parameters, period)
    )
    remove_head_of_household = create_remove_head_of_household_reform(
        parameters, period
    )
    increase_taxable_earnings_for_social_security_reform = (
        create_increase_taxable_earnings_for_social_security_reform(
            parameters, period
        )
    )
    medicare_and_investment_tax_increase = (
        create_medicare_and_investment_tax_increase_reform(parameters, period)
    )
    ctc_expansion = create_ctc_expansion_reform(parameters, period)

    abolish_federal_income_tax = create_abolish_federal_income_tax_reform(
        parameters, period
    )
    abolish_payroll_tax = create_abolish_payroll_tax_reform(parameters, period)
    reported_state_income_tax = create_reported_state_income_tax_reform(
        parameters, period
    )
    capital_gains_tax_increase = create_capital_gains_tax_increase_reform(
        parameters, period
    )
    halve_joint_eitc_phase_out_rate = (
        create_halve_joint_eitc_phase_out_rate_reform(parameters, period)
    )
    ny_wftc = create_ny_working_families_tax_credit_reform(parameters, period)
    ny_a04038_enhanced_escc_infants = (
        create_ny_a04038_enhanced_escc_infants_reform(parameters, period)
    )
    sc_h3492_eitc_refundable = create_sc_h3492_eitc_refundable_reform(
        parameters, period
    )
    ny_a06774_enhanced_cdcc = create_ny_a06774_enhanced_cdcc_reform(
        parameters, period
    )
    ny_s04487_newborn_credit = create_ny_s04487_newborn_credit_reform(
        parameters, period
    )

    middle_class_tax_credit = create_middle_class_tax_credit_reform(
        parameters, period
    )
    rent_relief_tax_credit = create_rent_relief_tax_credit_reform(
        parameters, period
    )
    end_child_poverty_act = create_end_child_poverty_act_reform(
        parameters, period
    )
    edaa_end_child_poverty_act = create_edaa_end_child_poverty_act_reform(
        parameters, period
    )
    boost_middle_class_tax_credit = (
        create_boost_middle_class_tax_credit_reform(parameters, period)
    )
    mn_walz_hf1938 = create_mn_walz_hf1938_repeal_reform(parameters, period)

    or_rebate_state_tax_exempt = create_or_rebate_state_tax_exempt_reform(
        parameters, period
    )
    family_security_act_2024_ctc = create_family_security_act_2024_ctc_reform(
        parameters, period
    )
    family_security_act_2024_eitc = (
        create_family_security_act_2024_eitc_reform(parameters, period)
    )
    repeal_dependent_exemptions = create_repeal_dependent_exemptions_reform(
        parameters, period
    )
    harris_capital_gains = create_harris_capital_gains_reform(
        parameters, period
    )
    tip_income_tax_exempt = create_tax_exempt_reform(parameters, period)
    repeal_state_dependent_exemptions = (
        create_repeal_state_dependent_exemptions_reform(parameters, period)
    )
    ctc_older_child_supplement = create_ctc_older_child_supplement_reform(
        parameters, period
    )
    abolish_snap_deductions = create_abolish_snap_deductions_reform(
        parameters, period
    )
    abolish_snap_net_income_test = create_abolish_snap_net_income_test_reform(
        parameters, period
    )
    dc_property_tax_credit = create_dc_property_tax_credit_reform(
        parameters, period
    )
    limit_salt_deduction_to_property_taxes = (
        create_limit_salt_deduction_to_property_taxes_reform(
            parameters, period
        )
    )
    nyc_school_tax_credit_with_phase_out = (
        create_nyc_school_tax_credit_with_phase_out_reform(parameters, period)
    )
    mt_ctc = create_mt_ctc_reform(parameters, period)
    fisc_act = create_fisc_act_reform(parameters, period)
    tax_employer_social_security_tax = (
        create_tax_employer_social_security_tax_reform(parameters, period)
    )
    tax_employer_medicare_tax = create_tax_employer_medicare_tax_reform(
        parameters, period
    )
    tax_employer_payroll_tax = create_tax_employer_payroll_tax_reform(
        parameters, period
    )
    afa_other_dependent_credit = create_afa_other_dependent_credit_reform(
        parameters, period
    )
    non_refundable_ss_credit = create_non_refundable_ss_credit_reform(
        parameters, period
    )
    senior_deduction_extension = create_senior_deduction_extension_reform(
        parameters, period
    )
    agi_surtax = create_agi_surtax_reform(parameters, period)

    reconciled_ssn_for_llc_and_aoc = (
        create_reconciled_ssn_for_llc_and_aoc_reform(parameters, period)
    )
    ctc_additional_bracket = create_ctc_additional_bracket_reform(
        parameters, period
    )
    additional_tax_bracket = create_additional_tax_bracket_reform(
        parameters, period
    )
    mi_surtax = create_mi_surtax_reform(parameters, period)

    nyc_mamdani_income_tax = create_nyc_mamdani_income_tax_reform(
        parameters, period
    )

    ut_refundable_eitc = create_ut_refundable_eitc_reform(parameters, period)

    ut_hb210 = create_ut_hb210_reform(parameters, period)

    ut_hb210_s2 = create_ut_hb210_s2_reform(parameters, period)

    american_worker_rebate_act = create_american_worker_rebate_act_reform(
        parameters, period
    )
    ctc_per_child_phase_out = create_ctc_per_child_phase_out_reform(
        parameters, period
    )
    ctc_per_child_phase_in = create_ctc_per_child_phase_in_reform(
        parameters, period
    )
    ctc_minimum_refundable_amount = (
        create_ctc_minimum_refundable_amount_reform(parameters, period)
    )
    ri_ctc = create_ri_ctc_reform(parameters, period)
    ri_exemption = create_ri_exemption_reform_fn(parameters, period)
    de_dependent_credit = create_de_dependent_credit_reform_fn(
        parameters, period
    )
    or_dependent_exemption_credit = (
        create_or_dependent_exemption_credit_reform_fn(parameters, period)
    )
    va_dependent_exemption = create_va_dependent_exemption_reform_fn(
        parameters, period
    )
    va_hb979 = create_va_hb979_reform(parameters, period)
    ct_refundable_ctc = create_ct_refundable_ctc_reform(parameters, period)
    aca_ptc_additional_bracket = create_aca_ptc_additional_bracket_reform(
        parameters, period
    )
    aca_ptc_simplified_bracket = create_aca_ptc_simplified_bracket_reform(
        parameters, period
    )
    aca_ptc_700_fpl_cliff = create_aca_ptc_700_fpl_cliff_reform(
        parameters, period
    )
    cdcc_single_parent_work_requirement = (
        create_cdcc_single_parent_work_requirement_reform(parameters, period)
    )
    ct_sb100 = create_ct_sb100_reform(parameters, period)
    ct_tax_rebate_2026 = create_ct_tax_rebate_2026_reform(parameters, period)
    ct_hb5009 = create_ct_hb5009_reform(parameters, period)

    reforms = [
        afa_reform,
        winship_reform,
        dc_kccatc_reform,
        dc_tax_threshold_joint_ratio_reform,
        remove_head_of_household,
        increase_taxable_earnings_for_social_security_reform,
        ctc_expansion,
        abolish_federal_income_tax,
        abolish_payroll_tax,
        reported_state_income_tax,
        medicare_and_investment_tax_increase,
        capital_gains_tax_increase,
        halve_joint_eitc_phase_out_rate,
        ny_wftc,
        ny_a04038_enhanced_escc_infants,
        sc_h3492_eitc_refundable,
        ny_a06774_enhanced_cdcc,
        ny_s04487_newborn_credit,
        middle_class_tax_credit,
        rent_relief_tax_credit,
        end_child_poverty_act,
        edaa_end_child_poverty_act,
        boost_middle_class_tax_credit,
        mn_walz_hf1938,
        or_rebate_state_tax_exempt,
        family_security_act_2024_ctc,
        family_security_act_2024_eitc,
        repeal_dependent_exemptions,
        harris_capital_gains,
        tip_income_tax_exempt,
        repeal_state_dependent_exemptions,
        ctc_older_child_supplement,
        abolish_snap_deductions,
        abolish_snap_net_income_test,
        dc_property_tax_credit,
        limit_salt_deduction_to_property_taxes,
        nyc_school_tax_credit_with_phase_out,
        mt_ctc,
        fisc_act,
        tax_employer_social_security_tax,
        tax_employer_medicare_tax,
        tax_employer_payroll_tax,
        afa_other_dependent_credit,
        non_refundable_ss_credit,
        senior_deduction_extension,
        agi_surtax,
        reconciled_ssn_for_llc_and_aoc,
        ctc_additional_bracket,
        mi_surtax,
        nyc_mamdani_income_tax,
        ut_refundable_eitc,
        ut_hb210,
        ut_hb210_s2,
        additional_tax_bracket,
        american_worker_rebate_act,
        ctc_per_child_phase_out,
        ctc_per_child_phase_in,
        ctc_minimum_refundable_amount,
        ri_ctc,
        ri_exemption,
        de_dependent_credit,
        or_dependent_exemption_credit,
        va_dependent_exemption,
        va_hb979,
        ct_refundable_ctc,
        aca_ptc_additional_bracket,
        aca_ptc_simplified_bracket,
        aca_ptc_700_fpl_cliff,
        cdcc_single_parent_work_requirement,
        ct_hb5009,
        ct_sb100,
        ct_tax_rebate_2026,
    ]
    reforms = tuple(filter(lambda x: x is not None, reforms))

    class combined_reform(Reform):
        def apply(self):
            for reform in reforms:
                reform.apply(self)

    return combined_reform
