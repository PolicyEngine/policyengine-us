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
from .harris.lift.middle_class_tax_credit import (
    create_middle_class_tax_credit_reform,
)
from .harris.rent_relief_act.rent_relief_tax_credit import (
    create_rent_relief_tax_credit_reform,
)
from .congress.tlaib import (
    create_end_child_poverty_act_reform,
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
from .salt_phase_out.salt_phase_out_reform import (
    create_salt_phase_out_reform,
)
from .state_dependent_exemptions import (
    create_repeal_state_dependent_exemptions_reform,
)
from .ctc import (
    create_ctc_older_child_supplement_reform,
    create_ctc_additional_bracket_reform,
)
from .second_earner import (
    create_second_earner_tax_reform,
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
    create_reconciled_qbid_reform,
    create_reconciled_pease_reform,
    create_reconciled_tip_and_overtime_exempt_reform,
    create_reconciled_auto_loan_interest_ald_reform,
    create_ctc_ssn_reform,
    create_reconciled_additional_senior_standard_deduction_reform,
    create_reconciled_ssn_for_llc_and_aoc_reform,
    create_aca_ptc_immigration_status_reform,
    create_reconciliation_qbid_with_floor_reform,
    create_reconciliation_cdcc_reform,
    create_reconciled_medicaid_work_requirement_reform,
    create_reconciled_snap_abawd_work_requirement_reform,
    create_reconciled_charitable_deduction_reform,
)
from .additional_tax_bracket import (
    create_additional_tax_bracket_reform,
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

    middle_class_tax_credit = create_middle_class_tax_credit_reform(
        parameters, period
    )
    rent_relief_tax_credit = create_rent_relief_tax_credit_reform(
        parameters, period
    )
    end_child_poverty_act = create_end_child_poverty_act_reform(
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
    salt_phase_out = create_salt_phase_out_reform(parameters, period)
    repeal_state_dependent_exemptions = (
        create_repeal_state_dependent_exemptions_reform(parameters, period)
    )
    ctc_older_child_supplement = create_ctc_older_child_supplement_reform(
        parameters, period
    )
    second_earner_tax_reform = create_second_earner_tax_reform(
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
    reconciled_qbid = create_reconciled_qbid_reform(parameters, period)
    reconciled_pease = create_reconciled_pease_reform(parameters, period)
    reconciled_tip_and_overtime_exempt = (
        create_reconciled_tip_and_overtime_exempt_reform(parameters, period)
    )
    reconciled_auto_loan_interest_ald = (
        create_reconciled_auto_loan_interest_ald_reform(parameters, period)
    )
    ctc_ssn = create_ctc_ssn_reform(parameters, period)
    reconciled_additional_senior_standard_deduction = (
        create_reconciled_additional_senior_standard_deduction_reform(
            parameters, period
        )
    )

    ctc_ssn = create_ctc_ssn_reform(parameters, period)
    reconciled_ssn_for_llc_and_aoc = (
        create_reconciled_ssn_for_llc_and_aoc_reform(parameters, period)
    )
    aca_ptc_immigration_status = create_aca_ptc_immigration_status_reform(
        parameters, period
    )
    reconciliation_qbid_with_floor = (
        create_reconciliation_qbid_with_floor_reform(parameters, period)
    )
    ctc_additional_bracket = create_ctc_additional_bracket_reform(
        parameters, period
    )
    reconciliation_cdcc = create_reconciliation_cdcc_reform(parameters, period)

    additional_tax_bracket = create_additional_tax_bracket_reform(
        parameters, period
    )
    reconciled_medicaid_work_requirement = (
        create_reconciled_medicaid_work_requirement_reform(parameters, period)
    )

    reconciled_snap_abawd_work_requirement = (
        create_reconciled_snap_abawd_work_requirement_reform(
            parameters, period
        )
    )
    reconciled_charitable_deduction = (
        create_reconciled_charitable_deduction_reform(parameters, period)
    )

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
        middle_class_tax_credit,
        rent_relief_tax_credit,
        end_child_poverty_act,
        boost_middle_class_tax_credit,
        mn_walz_hf1938,
        or_rebate_state_tax_exempt,
        family_security_act_2024_ctc,
        family_security_act_2024_eitc,
        repeal_dependent_exemptions,
        harris_capital_gains,
        tip_income_tax_exempt,
        salt_phase_out,
        repeal_state_dependent_exemptions,
        ctc_older_child_supplement,
        second_earner_tax_reform,
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
        reconciled_qbid,
        reconciled_pease,
        reconciled_tip_and_overtime_exempt,
        reconciled_auto_loan_interest_ald,
        ctc_ssn,
        reconciled_additional_senior_standard_deduction,
        reconciled_ssn_for_llc_and_aoc,
        aca_ptc_immigration_status,
        reconciliation_qbid_with_floor,
        ctc_additional_bracket,
        reconciliation_cdcc,
        additional_tax_bracket,
        reconciled_medicaid_work_requirement,
        reconciled_snap_abawd_work_requirement,
        reconciled_charitable_deduction,
    ]
    reforms = tuple(filter(lambda x: x is not None, reforms))

    class combined_reform(Reform):
        def apply(self):
            for reform in reforms:
                reform.apply(self)

    return combined_reform
