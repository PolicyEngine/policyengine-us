from policyengine_us.model_api import *


class wi_shares_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Wisconsin Shares countable income"
    definition_period = MONTH
    defined_for = StateCode.WI
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=58",
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=59",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wi.dcf.shares.income
        base_income = add(spm_unit, period, p.sources)
        # The earned income and SSI of minor dependents are disregarded
        # (Section 6.3); the earned income of a minor parent (a head or
        # spouse) still counts.
        person = spm_unit.members
        age = person("age", period.this_year)
        is_dependent = ~person("is_tax_unit_head_or_spouse", period.this_year)
        is_minor_dependent = (age < p.minor_income_disregard_age) & is_dependent
        minor_earned_income = spm_unit.sum(
            is_minor_dependent
            * add(
                person,
                period,
                [
                    "employment_income",
                    "self_employment_income",
                    "sstb_self_employment_income",
                    "farm_operations_income",
                    "partnership_s_corp_income",
                ],
            )
        )
        # SSI of adults in the assistance group is counted (Section 6.2); ssi
        # is not in the sources list so the minor-dependent disregard can be
        # applied here.
        counted_ssi = spm_unit.sum(~is_minor_dependent * person("ssi", period))
        # Court-ordered child and family support is fully disregarded when the
        # assistance group's monthly total is at or below the cap; when it
        # exceeds the cap, the entire amount counts (a cliff, not a
        # deduction; Sections 6.2 and 6.3).
        child_support = add(spm_unit, period, ["child_support_received"])
        counted_child_support = where(
            child_support > p.child_support_disregard_cap, child_support, 0
        )
        # Self-employment income is net earnings reported to the IRS; the
        # handbook's add-backs (depreciation, personal business expenses,
        # personal transportation, capital equipment purchases, and loan
        # principal payments; Section 6.4.4) have no PolicyEngine inputs. The
        # total is floored at zero so a self-employment loss cannot produce
        # negative countable income.
        return max_(
            base_income - minor_earned_income + counted_ssi + counted_child_support,
            0,
        )
