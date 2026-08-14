from policyengine_us.model_api import *


class ut_ccap_is_client(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Utah CCAP client"
    defined_for = StateCode.UT
    reference = (
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-702",
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-710",
    )

    def formula(person, period, parameters):
        # R986-700-702(2) makes the CC client a parent, specified relative,
        # or court-appointed guardian. is_parent (own children in the
        # household) rather than a tax-unit role flag identifies parent
        # clients across tax-unit boundaries and keeps a minor parent
        # visible; if both parents live in the household, both are clients
        # (R986-700-710(4)(a)). When no parent lives in the household, the
        # tax-unit head or spouse proxies the nonparent caretaker client
        # (R986-700-710(4)(b)). Co-resident relatives who are not the
        # client stay excluded. Foster parents receiving DHHS foster care
        # reimbursement are themselves eligible clients
        # (R986-700-702(2)(a); R986-700-710(3)(g) and (4)(c)), so
        # is_parent correctly includes them and no foster-parent carve-out
        # applies.
        is_parent = person("is_parent", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # person.spm_unit.sum already broadcasts the unit total back to
        # each member, so no explicit projection is needed.
        no_parent_present = person.spm_unit.sum(is_parent) == 0
        return is_parent | (no_parent_present & is_head_or_spouse)
