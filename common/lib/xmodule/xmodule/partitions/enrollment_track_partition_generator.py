"""
The enrollment_track dynamic partition generation to be part of the
openedx.dynamic_partition plugin.
"""
import logging

import six
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from xmodule.partitions.partitions import (
    get_partition_from_id,
    ENROLLMENT_TRACK_PARTITION_ID,
    UserPartition,
    UserPartitionError
)

log = logging.getLogger(__name__)

FEATURES = getattr(settings, 'FEATURES', {})


def create_enrollment_track_partition(course):
    """
    Create and return the dynamic enrollment track user partition.
    If it cannot be created, None is returned.
    """
    if not FEATURES.get('ENABLE_ENROLLMENT_TRACK_USER_PARTITION'):
        return None

    try:
        enrollment_track_scheme = UserPartition.get_scheme("enrollment_track")
    except UserPartitionError:
        log.warning("No 'enrollment_track' scheme registered, EnrollmentTrackUserPartition will not be created.")
        return None

    used_ids = set(p.id for p in course.user_partitions)
    if ENROLLMENT_TRACK_PARTITION_ID in used_ids:
        log.warning(
            "Can't add 'enrollment_track' partition, as ID {id} is assigned to {partition} in course {course}.".format(
                id=ENROLLMENT_TRACK_PARTITION_ID,
                partition=get_partition_from_id(course.user_partitions, ENROLLMENT_TRACK_PARTITION_ID).name,
                course=six.text_type(course.id)
            )
        )
        return None

    partition = enrollment_track_scheme.create_user_partition(
        id=ENROLLMENT_TRACK_PARTITION_ID,
        name=_(u"Enrollment Track Groups"),
        description=_(u"Partition for segmenting users by enrollment track"),
        parameters={"course_id": six.text_type(course.id)}
    )
    return partition
