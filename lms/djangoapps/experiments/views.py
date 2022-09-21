"""
Experimentation views
"""


from django.contrib.auth import get_user_model
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from lms.djangoapps.courseware import courses
from opaque_keys.edx.keys import CourseKey
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from common.djangoapps.util.json_request import JsonResponse

from lms.djangoapps.experiments import filters, serializers
from lms.djangoapps.experiments.models import ExperimentData, ExperimentKeyValue
from lms.djangoapps.experiments.permissions import IsStaffOrOwner, IsStaffOrReadOnly, IsStaffOrReadOnlyForSelf
from lms.djangoapps.experiments.utils import get_experiment_user_metadata_context
from openedx.core.djangoapps.cors_csrf.authentication import SessionAuthenticationCrossDomainCsrf
from common.djangoapps.student.models import get_user_by_username_or_email

User = get_user_model()  # pylint: disable=invalid-name


class ExperimentCrossDomainSessionAuth(SessionAuthenticationAllowInactiveUser, SessionAuthenticationCrossDomainCsrf):
    """Session authentication that allows inactive users and cross-domain requests. """
    pass


class ExperimentDataViewSet(viewsets.ModelViewSet):
    authentication_classes = (JwtAuthentication, ExperimentCrossDomainSessionAuth,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.ExperimentDataFilter
    permission_classes = (permissions.IsAuthenticated, IsStaffOrOwner,)
    queryset = ExperimentData.objects.all()
    serializer_class = serializers.ExperimentDataSerializer
    _cached_users = {}

    def filter_queryset(self, queryset):
        queryset = queryset.filter(user=self.request.user)
        return super(ExperimentDataViewSet, self).filter_queryset(queryset)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.ExperimentDataCreateSerializer
        return serializers.ExperimentDataSerializer

    def create_or_update(self, request, *args, **kwargs):
        # If we have a primary key, treat this as a regular update request
        if self.kwargs.get('pk'):
            return self.update(request, *args, **kwargs)

        # If we only have data, check to see if an instance exists in the database. If so, update it.
        # Otherwise, create a new instance.
        experiment_id = request.data.get('experiment_id')
        key = request.data.get('key')

        if experiment_id and key:
            try:
                obj = self.get_queryset().get(user=self.request.user, experiment_id=experiment_id, key=key)
                self.kwargs['pk'] = obj.pk
                return self.update(request, *args, **kwargs)
            except ExperimentData.DoesNotExist:
                pass

        self.action = 'create'
        return self.create(request, *args, **kwargs)

    def _cache_users(self, usernames):
        users = User.objects.filter(username__in=usernames)
        self._cached_users = {user.username: user for user in users}

    def _get_user(self, username):
        user = self._cached_users.get(username)

        if not user:
            user = User.objects.get(username=username)
            self._cached_users[username] = user

        return user


class ExperimentKeyValueViewSet(viewsets.ModelViewSet):
    authentication_classes = (JwtAuthentication, ExperimentCrossDomainSessionAuth,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.ExperimentKeyValueFilter
    permission_classes = (IsStaffOrReadOnly,)
    queryset = ExperimentKeyValue.objects.all()
    serializer_class = serializers.ExperimentKeyValueSerializer


class UserMetaDataView(APIView):
    authentication_classes = (JwtAuthentication, ExperimentCrossDomainSessionAuth,)
    permission_classes = (IsStaffOrReadOnlyForSelf,)

    def get(self, request, course_id=None, username=None):
        """ Return user-metadata for the given course and user """
        try:
            user = get_user_by_username_or_email(username)
        except User.DoesNotExist:
            # Note: this will only be seen by staff, for administrative de-bugging purposes
            message = "Provided user is not found"
            return JsonResponse({'message': message}, status=404)

        try:
            course = courses.get_course_by_id(CourseKey.from_string(course_id))
        except Http404:
            message = "Provided course is not found"
            return JsonResponse({'message': message}, status=404)

        context = get_experiment_user_metadata_context(course, user)
        user_metadata = context.get('user_metadata')
        return JsonResponse(user_metadata)
