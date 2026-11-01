from policyengine_us.model_api import *
from policyengine_us.tools.pinned_tbs import get_pre_arpa_eitc_tbs
from policyengine_us.variables.gov.states.ny.tax.income.adjusted_gross_income.ny_recomputed_federal_agi import (
    get_ny_recomputed_branch,
)


class ny_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/606",  # (d)
        "https://www.tax.ny.gov/pdf/2021/inc/it215i_2021.pdf",
        # 2020 IT-215 instructions: recompute the federal credit with line
        # 19a when lines 19 and 19a differ.
        "https://www.tax.ny.gov/pdf/2020/inc/it215i_2020.pdf#page=2",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits
        if p.eitc.decoupled:
            # NY decoupled from post-March 2020 IRC amendments for
            # TY 2021 (Tax Law 607(a), Part WWW Ch.58 Laws of 2020).
            # ARPA (March 11, 2021) expanded the federal EITC but NY
            # does not conform. Recompute the federal EITC with
            # pre-ARPA (2020) parameter values.
            simulation = tax_unit.simulation
            branch = get_branch_for_period(simulation, "ny_pre_arpa_eitc", period)
            branch.tax_benefit_system = get_pre_arpa_eitc_tbs(
                simulation.tax_benefit_system
            )
            for variable in branch.tax_benefit_system.variables:
                if "eitc" in variable:
                    branch.delete_arrays(variable)
            federal_eitc = branch.tax_unit("eitc", period)
        else:
            # IT-215: the federal credit recomputed with recomputed federal
            # AGI (IT-201 line 19a) when it differs from federal AGI.
            branch = get_ny_recomputed_branch(tax_unit, period)
            if branch is None:
                federal_eitc = tax_unit("eitc", period)
            else:
                federal_eitc = branch.calculate("eitc", period)
        tentative_nys_eitc = federal_eitc * p.eitc.match
        income_tax_before_credits = tax_unit("ny_income_tax_before_credits", period)
        household_credit = tax_unit("ny_household_credit", period)
        capped_household_credit = min_(income_tax_before_credits, household_credit)
        return max_(0, tentative_nys_eitc - capped_household_credit)
