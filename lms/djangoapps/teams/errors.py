"""
Errors thrown in the Team API.
"""


class TeamAPIRequestError(Exception):
    """There was a problem with a request to the Team API."""
    pass


class NotEnrolledInCourseForTeam(TeamAPIRequestError):
    """User is not enrolled in the course for the team they are trying to join."""
    pass


class AlreadyOnTeamInTeamset(TeamAPIRequestError):
    """User is already a member of another team in the same teamset."""
    pass


class AddToIncompatibleTeamError(TeamAPIRequestError):
    """
    User is enrolled in a mode that is incompatible with this team type.
    e.g. Masters learners cannot be placed in a team with audit learners
    """
    pass


class ElasticSearchConnectionError(TeamAPIRequestError):
    """The system was unable to connect to the configured elasticsearch instance."""
    pass


class ImmutableMembershipFieldException(Exception):
    """An attempt was made to change an immutable field on a CourseTeamMembership model."""
    pass
