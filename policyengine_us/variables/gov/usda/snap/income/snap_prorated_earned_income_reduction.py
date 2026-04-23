from policyengine_us.model_api import *


class snap_prorated_earned_income_reduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP prorated earned income reduction"
    unit = USD
    documentation = (
        "The portion of prorated-disqualified members' earned income "
        "that should not be counted per 7 CFR 273.11(c)(2) / (c)(3). "
        "The regulation divides the ineligible member's income evenly "
        "among all household members; only the portion that would go "
        "to eligible members is counted. This variable returns the "
        "amount to subtract from the raw SPM-unit earned income "
        "aggregation. It covers Person-level employment_income and "
        "self-employment income with the SPM-level expense deduction "
        "attributed pro rata across self-employed members. Zero when "
        "there are no prorated-disqualified members."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_2",
        "https://www.law.cornell.edu/cfr/text/7/273.11#c_3",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_prorated = person("is_snap_disqualified_prorated", period)
        countable = person("snap_countable_earner", period)
        spm_size = person.spm_unit("spm_unit_size", period)
        prorated_count = person.spm_unit.sum(is_prorated)
        safe_size = where(spm_size > 0, spm_size, 1)
        # Per 273.11(c)(2), divide income evenly across all members;
        # count only the eligible share. The excluded share is
        # prorated_count / spm_size of the prorated member's income.
        exclusion_fraction = prorated_count / safe_size
        employment = person("employment_income", period)
        self_emp_gross = add(
            person,
            period,
            [
                "self_employment_income_before_lsr",
                "sstb_self_employment_income_before_lsr",
            ],
        )
        spm_self_emp_gross = person.spm_unit.sum(self_emp_gross)
        spm_expense = person.spm_unit("snap_self_employment_expense_deduction", period)
        # Attribute the SPM-level expense deduction proportionally to
        # each member's share of total self-employment gross income.
        safe_gross = where(spm_self_emp_gross > 0, spm_self_emp_gross, 1)
        attributed_expense = where(
            spm_self_emp_gross > 0,
            spm_expense * self_emp_gross / safe_gross,
            0,
        )
        self_emp_net_person = max_(self_emp_gross - attributed_expense, 0)
        person_earned = (employment + self_emp_net_person) * countable
        reduction_per_person = person_earned * is_prorated * exclusion_fraction
        return spm_unit.sum(reduction_per_person)
