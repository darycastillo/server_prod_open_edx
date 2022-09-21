"""
Unit tests for the Course Blocks signals
"""


import ddt
from edx_toggles.toggles.testutils import override_waffle_switch
from mock import patch
from opaque_keys.edx.locator import CourseLocator, LibraryLocator
from xmodule.modulestore.exceptions import ItemNotFoundError
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from ..api import get_block_structure_manager
from ..config import INVALIDATE_CACHE_ON_PUBLISH, waffle_switch
from ..signals import update_block_structure_on_course_publish
from .helpers import is_course_in_block_structure_cache


@ddt.ddt
class CourseBlocksSignalTest(ModuleStoreTestCase):
    """
    Tests for the Course Blocks signal
    """
    ENABLED_SIGNALS = ['course_deleted', 'course_published']

    def setUp(self):
        super(CourseBlocksSignalTest, self).setUp()
        self.course = CourseFactory.create()
        self.course_usage_key = self.store.make_course_usage_key(self.course.id)

    def test_course_update(self):
        test_display_name = "Lightsabers 101"

        # Course exists in cache initially
        bs_manager = get_block_structure_manager(self.course.id)
        orig_block_structure = bs_manager.get_collected()
        self.assertTrue(is_course_in_block_structure_cache(self.course.id, self.store))
        self.assertNotEqual(
            test_display_name,
            orig_block_structure.get_xblock_field(self.course_usage_key, 'display_name')
        )

        self.course.display_name = test_display_name
        self.store.update_item(self.course, self.user.id)

        # Cached version of course has been updated
        updated_block_structure = bs_manager.get_collected()
        self.assertEqual(
            test_display_name,
            updated_block_structure.get_xblock_field(self.course_usage_key, 'display_name')
        )

    @ddt.data(True, False)
    @patch('openedx.core.djangoapps.content.block_structure.manager.BlockStructureManager.clear')
    def test_cache_invalidation(self, invalidate_cache_enabled, mock_bs_manager_clear):
        test_display_name = "Jedi 101"

        with override_waffle_switch(waffle_switch(INVALIDATE_CACHE_ON_PUBLISH), active=invalidate_cache_enabled):
            self.course.display_name = test_display_name
            self.store.update_item(self.course, self.user.id)

        self.assertEqual(mock_bs_manager_clear.called, invalidate_cache_enabled)

    def test_course_delete(self):
        bs_manager = get_block_structure_manager(self.course.id)
        self.assertIsNotNone(bs_manager.get_collected())
        self.assertTrue(is_course_in_block_structure_cache(self.course.id, self.store))

        self.store.delete_course(self.course.id, self.user.id)
        with self.assertRaises(ItemNotFoundError):
            bs_manager.get_collected()

        self.assertFalse(is_course_in_block_structure_cache(self.course.id, self.store))

    @ddt.data(
        (CourseLocator(org='org', course='course', run='run'), True),
        (LibraryLocator(org='org', library='course'), False),
    )
    @ddt.unpack
    @patch('openedx.core.djangoapps.content.block_structure.tasks.update_course_in_cache_v2.apply_async')
    def test_update_only_for_courses(self, key, expect_update_called, mock_update):
        update_block_structure_on_course_publish(sender=None, course_key=key)
        self.assertEqual(mock_update.called, expect_update_called)
