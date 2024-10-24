from .congress.delauro import create_american_family_act_with_baby_bonus_reform
from .dc_kccatc import create_dc_kccatc_reform
from .winship import create_eitc_winship_reform
from .dc_tax_threshold_joint_ratio import (
    create_dc_tax_threshold_joint_ratio_reform,
)
from .congress.romney.family_security_act import (
    create_remove_head_of_household,
)
from .cbo.payroll import (
    create_increase_taxable_earnings_for_social_security_reform,
)
from .congress.wyden_smith import create_ctc_expansion
from .federal import create_abolish_federal_income_tax
from .federal import create_abolish_payroll_tax
from .federal import create_reported_state_income_tax
from .biden.budget_2025 import (
    create_medicare_and_investment_tax_increase_reform,
)
from .biden.budget_2025 import create_capital_gains_tax_increase
from .eitc import create_halve_joint_eitc_phase_out_rate
from .states.ny.wftc import create_ny_working_families_tax_credit
from .states.dc.dc_ctc import (
    create_dc_ctc,
)
from .harris.lift.middle_class_tax_credit import (
    create_middle_class_tax_credit,
)
from .harris.rent_relief_act.rent_relief_tax_credit import (
    create_rent_relief_tax_credit,
)
from .congress.tlaib import (
    create_end_child_poverty_act,
)
from .congress.tlaib.boost import (
    create_boost_middle_class_tax_credit,
)
from .states.mn.walz import (
    create_mn_walz_hf1938_repeal,
)
from .states.oregon.rebate import (
    create_or_rebate_state_tax_exempt,
)
from .congress.romney.family_security_act_2024.ctc import (
    create_family_security_act_2024_ctc,
)
from .congress.romney.family_security_act_2024.eitc import (
    create_family_security_act_2024_eitc,
)
from .treasury.repeal_dependent_exemptions import (
    create_repeal_dependent_exemptions,
)
from .harris.capital_gains import (
    create_harris_capital_gains_reform,
)
from .tax_exempt.tax_exempt_reform import (
    create_tax_exempt_reform,
)


from policyengine_core.reforms import Reform
import warnings
from policyengine_us.reforms.utils import create_reform_if_active


def create_structural_reforms_from_parameters(parameters, period):
    afa_reform = create_american_family_act_with_baby_bonus_reform(
        parameters, period
    )
    winship_reform = create_eitc_winship_reform(parameters, period)
    dc_kccatc_reform = create_dc_kccatc_reform(parameters, period)
    dc_tax_threshold_joint_ratio_reform = (
        create_dc_tax_threshold_joint_ratio_reform(parameters, period)
    )
    remove_head_of_household = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.congress.romney.family_security_act.remove_head_of_household",
        create_remove_head_of_household,
        bypass=True,
    )
    increase_taxable_earnings_for_social_security_reform = (
        create_increase_taxable_earnings_for_social_security_reform(
            parameters, period
        )
    )
    medicare_and_investment_tax_increase = (
        create_medicare_and_investment_tax_increase_reform(parameters, period)
    )
    ctc_expansion = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.congress.wyden_smith",
        create_ctc_expansion,
        bypass=True,
    )

    abolish_federal_income_tax = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.ubi_center.flat_tax.abolish_federal_income_tax",
        create_abolish_federal_income_tax,
        bypass=True,
    )
    abolish_payroll_tax = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.ubi_center.flat_tax.abolish_payroll_tax",
        create_abolish_payroll_tax,
        bypass=True,
    )
    reported_state_income_tax = create_reform_if_active(
        parameters,
        period,
        "simulation.reported_state_income_tax",
        create_reported_state_income_tax,
        bypass=True,
    )
    capital_gains_tax_increase = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.biden.budget_2025.capital_gains.active",
        create_capital_gains_tax_increase,
        bypass=True,
    )
    halve_joint_eitc_phase_out_rate = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.joint_eitc.in_effect",
        create_halve_joint_eitc_phase_out_rate,
        bypass=True,
    )
    ny_wftc = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.states.ny.wftc.in_effect",
        create_ny_working_families_tax_credit,
        bypass=True,
    )

    dc_ctc = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.states.dc.ctc.in_effect",
        create_dc_ctc,
        bypass=True,
    )

    middle_class_tax_credit = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.harris.lift.middle_class_tax_credit.in_effect",
        create_middle_class_tax_credit,
        bypass=True,
    )
    rent_relief_tax_credit = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.harris.rent_relief_act.rent_relief_credit.in_effect",
        create_rent_relief_tax_credit,
        bypass=True,
    )
    end_child_poverty_act = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.congress.tlaib.end_child_poverty_act.in_effect",
        create_end_child_poverty_act,
        bypass=True,
    )
    boost_middle_class_tax_credit = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.harris.lift.middle_class_tax_credit.in_effect",
        create_boost_middle_class_tax_credit,
        bypass=True,
    )
    mn_walz_hf1938 = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.states.mn.walz.hf1938.repeal",
        create_mn_walz_hf1938_repeal,
        bypass=True,
    )

    or_rebate_state_tax_exempt = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.states.or.rebate.state_tax_exempt",
        create_or_rebate_state_tax_exempt,
        bypass=True,
    )
    family_security_act_2024_ctc = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.congress.romney.family_security_act_2_0.ctc.apply_ctc_structure",
        create_family_security_act_2024_ctc,
        bypass=True,
    )
    family_security_act_2024_eitc = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.congress.romney.family_security_act_2_0.eitc.apply_eitc_structure",
        create_family_security_act_2024_eitc,
        bypass=True,
    )
    repeal_dependent_exemptions = create_reform_if_active(
        parameters,
        period,
        "gov.contrib.treasury.repeal_dependent_exemptions",
        create_repeal_dependent_exemptions,
        bypass=True,
    )
    harris_capital_gains = create_harris_capital_gains_reform(
        parameters, period
    )
    tip_income_tax_exempt = create_tax_exempt_reform(parameters, period)

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
        dc_ctc,
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
    ]
    reforms = tuple(filter(lambda x: x is not None, reforms))

    class combined_reform(Reform):
        def apply(self):
            for reform in reforms:
                reform.apply(self)

    return combined_reform
