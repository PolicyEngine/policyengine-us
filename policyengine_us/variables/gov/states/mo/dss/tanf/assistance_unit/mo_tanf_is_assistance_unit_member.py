from policyengine_us.model_api import *


class mo_tanf_is_assistance_unit_member(Variable):
    value_type = bool
    entity = Person
    label = "Missouri TANF assistance unit member"
    definition_period = MONTH
    reference = (
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-10/",
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        # Per DSS Manual 0210.005.10, the assistance unit contains the
        # dependent child(ren) and their parent(s) or caretaker relative.
        # Household members who are not dependent children — including
        # siblings age 19 and over — are excluded from the unit's needs.
        # Per 13 CSR 40-2.310(1)(F), SSI recipients are excluded entirely:
        # neither their needs nor their income count. Reported receipt
        # (receives_ssi) also excludes, covering people the model computes
        # as $0. Their resources cannot be excluded because assets are
        # modeled at the SPM-unit level only.
        is_ssi_recipient = (person("ssi", period) > 0) | person("receives_ssi", period)
        dependent_child = person("mo_tanf_dependent_child", period)
        eligible_child = dependent_child & ~is_ssi_recipient
        head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        # The dependent-flag guard keeps adult children who are claimed as
        # tax dependents from being counted as caretakers when the spouse
        # inference ranks them as the second adult.
        caretaker = (
            head_or_spouse
            & ~is_dependent
            & ~is_ssi_recipient
            & person.tax_unit.any(eligible_child)
        )
        return eligible_child | caretaker
