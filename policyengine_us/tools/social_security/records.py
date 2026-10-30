"""Resolve explicitly supplied worker computation bases without age proxies."""

import numpy as np


def resolve_worker_basis(person, period, component, active):
    """Return computation years, link flags and worker indices for each person.

    A recipient's component-specific computation year takes precedence over a
    linked worker's supplied basis. If both are present they must agree. Links
    read the worker's same-component year, then the shared computation-year
    input; auxiliary links may also use the worker's retirement-specific year.
    Unlinked own retirement/disability records may use their own shared year.

    Missing years remain zero. In particular, no recipient-age proxy is applied
    here. Invalid links and conflicting years are rejected only for ``active``
    records, so an unused source cannot disturb a selected calculation route.
    The returned arrays are private copies and never mutate stored inputs.
    """
    prefix = f"social_security_{component}"
    supplied_years = np.asarray(
        person(f"{prefix}_worker_eligibility_year", period), dtype=int
    )
    years = supplied_years.copy()
    shared = person("social_security_worker_computation_year", period)
    identifiers = person(f"{prefix}_worker_id", period)
    known = {str(identifier): i for i, identifier in enumerate(person.ids)}
    linked = np.zeros(len(years), dtype=bool)
    worker_indices = np.arange(len(years), dtype=int)
    auxiliary_years = (
        person("social_security_retirement_worker_eligibility_year", period)
        if component in ("survivors", "dependents")
        else None
    )
    for i in np.flatnonzero(active):
        identifier = str(identifiers[i])
        if not identifier:
            if component in ("retirement", "disability"):
                years[i] = years[i] or shared[i]
            continue
        if identifier not in known:
            raise ValueError("Social Security worker_id does not identify a person")
        j = known[identifier]
        worker_indices[i] = j
        record_year = supplied_years[j] or shared[j]
        if not record_year and auxiliary_years is not None:
            record_year = auxiliary_years[j]
        if years[i] and record_year and years[i] != record_year:
            raise ValueError("Conflicting supplied and linked worker computation years")
        years[i] = years[i] or record_year
        linked[i] = True
    return years, linked, worker_indices
