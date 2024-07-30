from django.db import IntegrityError
from django.test import TestCase

from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from organizations.models import Membership
from organizations.tests import create_organization, create_membership

from projects.models import ProjectMembership
from projects.tests import create_projects, create_project_membership

from tasks.models import Columns

from users.tests import create_user

LIST_CREATE_COLUMNS_URL = reverse('tasks:columns_list_create')
DETAIL_UPDATE_DELETE_COLUMN_URL = reverse(
    'tasks:column_detail', kwargs={'pk': 1})


def create_column(**params):
    return Columns.objects.create(**params)


class ColumnModelTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )

        self.organization = create_organization(
            name='Test Organization',
            domain='testorg.com',
        )

        self.organization_membership = create_membership(
            organization=self.organization,
            user=self.user,
            role=Membership.ROLE_OWNER
        )

        self.project = create_projects(
            name='Test Project',
            description='Test Description',
            organization=self.organization
        )

        self.project_membership = create_project_membership(
            project=self.project,
            user=self.user,
            role=ProjectMembership.PROJECT_MANAGER
        )

    def test_create_column_successful(self):
        data = {
            'project': self.project,
            'name': 'To Do',
            'position': 1
        }

        column = create_column(**data)

        self.assertEqual(column.project, self.project)
        self.assertEqual(column.name, 'To Do')
        self.assertEqual(column.position, 1)

    def test_create_column_without_project(self):
        with self.assertRaises(IntegrityError):
            create_column(
                name='To Do',
                position=1
            )


class PublicTaskApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.user = create_user(
            email='test@xample.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )

        self.organization = create_organization(
            name='Test Organization',
            domain='testorg.com'
        )

        self.organization_membership = create_membership(
            organization=self.organization,
            user=self.user,
            role=Membership.ROLE_OWNER
        )

        self.project = create_projects(
            name='Test Project',
            description='Test Description',
            organization=self.organization
        )

        self.project_membership = create_project_membership(
            project=self.project,
            user=self.user,
            role=ProjectMembership.PROJECT_MANAGER
        )

    def test_list_columns_unauthenticated(self):
        res = self.client.get(LIST_CREATE_COLUMNS_URL, {
            'project': self.project.id})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_column_unauthenticated(self):
        res = self.client.post(LIST_CREATE_COLUMNS_URL, {
            'project': self.project.id,
            'name': 'To Do',
            'position': 1
        })

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTaskApiTest(TestCase):
    def setUp(self) -> None:
        self.manager = APIClient()
        self.member = APIClient()
        self.external = APIClient()

        self.user = create_user(
            email='test@xample.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )

        self.user_member = create_user(
            email='test2@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Doe'
        )

        self.user_external = create_user(
            email='test3@example.com',
            password='testpass123',
            first_name='Juan',
            last_name='Dela Cruz'
        )

        self.organization = create_organization(
            name='Test Organization',
            domain='testorg.com'
        )

        self.organization2 = create_organization(
            name='Test Organization 2',
            domain='testorg2.com'
        )

        self.organization_membership = create_membership(
            organization=self.organization,
            user=self.user,
            role=Membership.ROLE_OWNER
        )

        self.organization_membership2 = create_membership(
            organization=self.organization,
            user=self.user_member,
            role=Membership.ROLE_MEMBER
        )

        self.organization_membership3 = create_membership(
            organization=self.organization2,
            user=self.user_external,
            role=Membership.ROLE_OWNER
        )

        self.project = create_projects(
            name='Test Project',
            description='Test Description',
            organization=self.organization
        )

        self.project_membership = create_project_membership(
            project=self.project,
            user=self.user,
            role=ProjectMembership.PROJECT_MANAGER
        )

        self.project_membership2 = create_project_membership(
            project=self.project,
            user=self.user_member,
            role=ProjectMembership.PROJECT_MEMBER
        )

        self.manager.force_authenticate(user=self.user)
        self.member.force_authenticate(user=self.user_member)
        self.external.force_authenticate(user=self.user_external)

    def test_create_column_successful(self):
        data = {
            'project': self.project.id,
            'name': 'To Do',
            'position': 1
        }

        res = self.manager.post(LIST_CREATE_COLUMNS_URL, data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_column_without_project(self):
        data = {
            'name': 'To Do',
            'position': 1
        }

        res = self.manager.post(LIST_CREATE_COLUMNS_URL, data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_column_unauthorized(self):
        """ Only project managers can create columns """
        data = {
            'project': self.project.id,
            'name': 'To Do',
            'position': 1
        }

        res = self.member.post(LIST_CREATE_COLUMNS_URL, data)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_columns_successful(self):

        data = {
            'project': self.project,
            'name': 'To Do',
            'position': 1
        }

        create_column(**data)

        res = self.manager.get(LIST_CREATE_COLUMNS_URL, {
                               'project_id': self.project.id})

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.member.get(LIST_CREATE_COLUMNS_URL, {
            'project_id': self.project.id})

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_columns_unauthorized(self):
        """ Only project members can list columns """
        res = self.external.get(LIST_CREATE_COLUMNS_URL, {
            'project_id': self.project.id})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_column_successful(self):
        data = {
            'project': self.project,
            'name': 'To Do',
            'position': 1
        }

        create_column(**data)

        data = {
            'name': 'In Progress',
            'position': 2
        }

        res = self.manager.patch(
            DETAIL_UPDATE_DELETE_COLUMN_URL, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_column_unauthorized(self):
        """ Only project managers can update columns """
        data = {
            'project': self.project,
            'name': 'To Do',
            'position': 1
        }

        create_column(**data)

        data = {
            'name': 'In Progress',
            'position': 2
        }

        res = self.member.patch(
            DETAIL_UPDATE_DELETE_COLUMN_URL, data)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_column_successful(self):
        data = {
            'project': self.project,
            'name': 'To Do',
            'position': 1
        }

        create_column(**data)

        res = self.manager.delete(DETAIL_UPDATE_DELETE_COLUMN_URL)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_column_unauthorized(self):
        """ Only project managers can delete columns """
        data = {
            'project': self.project,
            'name': 'To Do',
            'position': 1
        }

        create_column(**data)

        res = self.member.delete(DETAIL_UPDATE_DELETE_COLUMN_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
