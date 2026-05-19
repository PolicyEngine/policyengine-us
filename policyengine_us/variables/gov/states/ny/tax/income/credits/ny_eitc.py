from policyengine_us.model_api import *
from policyengine_core.periods import instant


class ny_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/606",  # (d)
        "https://www.tax.ny.gov/pdf/2021/inc/it215i_2021.pdf",
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
            branch = simulation.get_branch("ny_pre_arpa_eitc")
            branch.tax_benefit_system = simulation.tax_benefit_system.clone()
            branch_params = branch.tax_benefit_system.parameters
            pin_date = instant("2020-01-01")
            start = instant("2021-01-01")
            stop = instant("2021-12-31")
            eitc_node = branch_params.gov.irs.credits.eitc
            for param in eitc_node.get_descendants():
                if isinstance(param, Parameter):
                    try:
                        value = param(pin_date)
                        param.update(start=start, stop=stop, value=value)
                    except Exception:
                        pass
            for variable in branch.tax_benefit_system.variables:
                if "eitc" in variable:
                    branch.delete_arrays(variable)
            federal_eitc = branch.tax_unit("eitc", period)
        else:
            federal_eitc = tax_unit("eitc", period)
        tentative_nys_eitc = federal_eitc * p.eitc.match
        income_tax_before_credits = tax_unit("ny_income_tax_before_credits", period)
        household_credit = tax_unit("ny_household_credit", period)
        capped_household_credit = min_(income_tax_before_credits, household_credit)
        return max_(0, tentative_nys_eitc - capped_household_credit)
