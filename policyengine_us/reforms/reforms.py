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
    ]
    reforms = tuple(filter(lambda x: x is not None, reforms))

    class combined_reform(Reform):
        def apply(self):
            for reform in reforms:
                reform.apply(self)

    return combined_reform
