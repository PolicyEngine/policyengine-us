from policyengine_us.model_api import *


class id_retirement_benefits_deduction_disabled(Variable):
    value_type = bool
    entity = Person
    label = "Classified as disabled for the Idaho retirement benefits deduction"
    documentation = """
    Idaho Code 63-3022A(4): "As used in this section, the word "disabled"
    shall mean an individual who is a disabled person described in section
    63-701, Idaho Code, or an individual who qualifies as a person with a
    "permanent disability" under section 49-117(7)(b)(iv), Idaho Code." The
    definition applies to the whole section, so it governs both the test of
    63-3022A(1)(a) (age 62 and classified as disabled) and, from 2025, the
    disability test for military retirement benefits in (1)(b)(i). Before
    2025 the same definition was 63-3022A(d).

    Section 63-701(1)(d) describes "A disabled person who is recognized as
    disabled by the social security administration pursuant to title 42 of
    the United States Code", by the Railroad Retirement Board, or by "the
    office of management and budget pursuant to title 5", or, "if a person is
    not within the purview of, and is therefore not recognized as disabled
    by, any other entity listed in this paragraph", by the public employee
    retirement system or disability plan in which the person participates;
    63-701(1)(e), a disabled veteran of any war whose disability the
    Department of Veterans Affairs recognizes as service-connected to a
    degree of 10% or more, or who has a VA pension for nonservice-connected
    disabilities. Section 49-117(7)(b)(iv) describes a person whose physician
    certifies a mobility disability with "no expectation for a fundamental or
    marked change". The Form 39R instructions for 2024 and 2025 list the same
    groups, without the public employee plan.

    By default a person is classified as disabled if they receive Social
    Security disability insurance benefits (an award is the Social Security
    Administration's finding of disability) or are a veteran fully disabled
    by a service-connected disability (the model doesn't check
    63-701(1)(e)'s wartime service). Three more defaults are stand-ins, not
    recognitions the statute lists. Meeting the SSI disability test of 42
    U.S.C. 1382c(a)(3) (is_ssi_disabled) and permanent and total disability
    under 26 U.S.C. 22(e)(3) (is_permanently_and_totally_disabled) stand in
    for the Social Security Administration's recognition, which the model
    observes only through a benefit. is_disabled stands in for the groups
    PolicyEngine has no input for (a VA rating of 10% to 90%, a VA
    disability pension, a Railroad Retirement or title 5 disability annuity,
    a public employee plan's finding, a physician's certificate), as it did
    for this deduction before the variable existed; it can also admit a
    disability that no listed group covers. Blindness alone doesn't count:
    63-701(1)(g) lists it as a separate group, not as a disabled person.

    Set this variable to override the default, for example to false for a
    disability no listed body has recognized. Once any person has an input
    for a year, enter one for every head or spouse it applies to: people
    without an input get false, not the default.
    """
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/",
        "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch7/sect63-701/",
        "https://legislature.idaho.gov/statutesrules/idstat/title49/t49ch1/sect49-117/",
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=45",
    )

    def formula(person, period, parameters):
        # 63-701(1)(d): recognized as disabled by the Social Security
        # Administration under title 42, which a disability insurance award
        # shows.
        receives_ssdi = person("social_security_disability", period) > 0
        # 63-701(1)(e): a VA service-connected disability of 10% or more.
        service_connected = person(
            "is_fully_disabled_service_connected_veteran", period
        )
        # Stand-ins, not listed recognitions: the SSI disability test and
        # permanent and total disability for the Social Security
        # Administration's recognition, and is_disabled for the groups
        # PolicyEngine has no input for.
        stand_in = (
            person("is_ssi_disabled", period)
            | person("is_permanently_and_totally_disabled", period)
            | person("is_disabled", period)
        )
        return receives_ssdi | service_connected | stand_in
