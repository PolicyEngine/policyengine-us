from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    household_has_parent_ids,
    tax_unit_parent_indices,
)


class ar_personal_credit_disabled_dependent(Variable):
    value_type = float
    entity = Person
    label = "Arkansas disabled dependent personal tax credit amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dfa.arkansas.gov/wp-content/uploads/2021_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR1000F_FullYearResidentIndividualIncomeTaxReturn.pdf#page=1",
        "https://www.dfa.arkansas.gov/wp-content/uploads/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=12",
        "https://www.arkleg.state.ar.us/Home/FTPDocument?path=%2FACTS%2F1999%2FPublic%2FACT417.pdf#page=2",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.AR

    def formula(person, period, parameters):
        dependent = person("is_tax_unit_dependent", period)
        disabled = person("is_disabled", period)
        # The credit covers an individual who is "a child of the taxpayer's
        # blood, an adopted child, or a dependent" in the IRC 152 sense (Act
        # 417 of 1999). A return on which the filer (or, if joint, either
        # spouse) can be claimed as a dependent has no IRC 152 dependents
        # (IRC 152(b)(1)), so only the filers' own children still qualify.
        filer_is_dependent = person.tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        # A filer's child: a parent id that names a head or spouse of the
        # tax unit. Parent ids also name step-parents, which on a joint
        # return covers the other spouse's own child. Without parent ids the
        # model cannot tell a filer's child from another dependent and keeps
        # the child route open.
        filer = person("is_tax_unit_head_or_spouse", period)
        first, second = tax_unit_parent_indices(person, period)
        child_of_filer = np.where(first >= 0, filer[first], False) | np.where(
            second >= 0, filer[second], False
        )
        relationship_unknown = ~household_has_parent_ids(person, period)
        qualifies = ~filer_is_dependent | child_of_filer | relationship_unknown
        disabled_dependent = disabled & dependent & qualifies
        p = parameters(period).gov.states.ar.tax.income.credits.personal.amount
        return disabled_dependent * p.disabled_dependent
