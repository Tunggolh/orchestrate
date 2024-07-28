from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from organizations.models import Organization, Membership
from organizations.tests import create_organization, create_membership
from users.tests import create_user
from .models import Projects, ProjectMembership


LIST_CREATE_PROJECT_URL = reverse('projects:list_create')
DETAIL_PROJECT_URL = reverse('projects:detail', kwargs={'pk': 1})
MEMBERS_PROJECT_URL = reverse('projects:members', kwargs={'pk': 1})
ADD_MEMBER_URL = reverse('projects:add_member', kwargs={'pk': 1})
REMOVE_MEMBER_URL = reverse('projects:remove_member', kwargs={'pk': 1})


def create_projects(**params):
    return Projects.objects.create(**params)


def create_project_membership(**params):
    return ProjectMembership.objects.create(**params)


class ProjectModelTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )
        self.organization = create_organization(
            name='Test Organization',
            domain='test.com'
        )

    def test_create_project_successful(self):
        name = 'Test Project'
        description = 'Test Description'
        project = Projects.objects.create(
            name=name,
            description=description,
            organization=self.organization
        )

        self.assertEqual(project.name, name)
        self.assertEqual(project.description, description)
        self.assertEqual(project.organization, self.organization)


class ProjectMembershipModelTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )

    def test_create_project_membership_successful(self):
        organization = create_organization(
            name='Test Organization',
            domain='test.com'
        )

        project = create_projects(
            name='Test Project',
            description='Test Description',
            organization=organization
        )

        member = ProjectMembership.objects.create(
            user=self.user,
            project=project,
            role=ProjectMembership.PROJECT_MANAGER
        )

        self.assertEqual(member.user, self.user)
        self.assertEqual(member.project, project)
        self.assertEqual(member.role, ProjectMembership.PROJECT_MANAGER)


class PublicProjectApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_project_unauthorized(self):
        payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': 1
        }

        res = self.client.post(LIST_CREATE_PROJECT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_projects_unauthorized(self):
        res = self.client.get(LIST_CREATE_PROJECT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_detail_projects_unauthorized(self):
        res = self.client.get(DETAIL_PROJECT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_member_to_project_unauthorized(self):
        payload = {
            'project': 1,
            'user': 1,
            'role': ProjectMembership.PROJECT_MANAGER
        }

        res = self.client.post(ADD_MEMBER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProjectApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )

        self.user2 = create_user(
            email='test2@example.com',
            first_name='Jane',
            last_name='Doe',
            password='testpass123'
        )

        self.user3 = create_user(
            email='test3@example.com',
            first_name='Jane',
            last_name='Doe',
            password='testpass123'
        )

        self.owner = APIClient()
        self.member = APIClient()
        self.member2 = APIClient()

        self.organization = create_organization(
            name='Test Organization',
            domain='test.com'
        )

        self.owner.force_authenticate(self.user)
        self.member.force_authenticate(self.user2)

        create_membership(
            user=self.user,
            organization=self.organization,
            role=Membership.ROLE_OWNER
        )

        create_membership(
            user=self.user2,
            organization=self.organization,
            role=Membership.ROLE_MEMBER
        )

        self.owner2 = APIClient()
        self.owner2.force_authenticate(self.user2)

        self.organization2 = create_organization(
            name='Test Organization 2',
            domain='test2.com'
        )

        create_membership(
            user=self.user2,
            organization=self.organization2,
            role=Membership.ROLE_OWNER
        )

        self.owner3 = APIClient()
        self.owner3.force_authenticate(self.user3)

    def test_create_project_successful(self):
        payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization.id
        }

        res = self.owner.post(LIST_CREATE_PROJECT_URL, payload)

        self.assertEqual(res.status_code, 201)

    def test_create_project_unauthorized(self):
        payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization.id
        }

        res = self.member.post(LIST_CREATE_PROJECT_URL, payload)

        self.assertEqual(res.status_code, 403)

    def test_create_project_not_in_organization(self):
        payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization2.id
        }

        res = self.owner.post(LIST_CREATE_PROJECT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_projects_successful(self):
        payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization.id
        }

        payload2 = {
            'name': 'Test Project 2',
            'description': 'Test Description 2',
            'organization': self.organization2.id
        }

        self.owner.post(LIST_CREATE_PROJECT_URL, payload)
        self.owner2.post(LIST_CREATE_PROJECT_URL, payload2)

        res = self.owner.get(LIST_CREATE_PROJECT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_retrieve_detail_projects_successful(self):
        payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization.id
        }

        project = self.owner.post(LIST_CREATE_PROJECT_URL, payload)

        res = self.owner.get(DETAIL_PROJECT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data['name'], project.data['name'])
        self.assertEqual(res.data['description'], project.data['description'])
        self.assertEqual(res.data['organization'],
                         project.data['organization'])

    def test_retrieve_detail_projects_unauthorized(self):
        payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization.id
        }

        self.owner.post(LIST_CREATE_PROJECT_URL, payload)

        res = self.owner2.get(DETAIL_PROJECT_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_project_successful(self):
        payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization.id
        }

        self.owner.post(LIST_CREATE_PROJECT_URL, payload)

        payload = {
            'name': 'Updated Test Project',
            'description': 'Updated Test Description'
        }

        res = self.owner.patch(DETAIL_PROJECT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data['name'], payload['name'])
        self.assertEqual(res.data['description'], payload['description'])

    def test_update_project_unauthorized(self):
        payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization.id
        }

        self.owner.post(LIST_CREATE_PROJECT_URL, payload)

        payload = {
            'name': 'Updated Test Project',
            'description': 'Updated Test Description'
        }

        res = self.member.patch(DETAIL_PROJECT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_project_members_successful(self):
        payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization.id
        }

        self.owner.post(LIST_CREATE_PROJECT_URL, payload)

        res = self.owner.get(MEMBERS_PROJECT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_add_member_to_project_successful(self):
        project_payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization.id
        }

        project = self.owner.post(LIST_CREATE_PROJECT_URL, project_payload)

        project_members = ProjectMembership.objects.filter(
            id=project.data.get('id'))

        self.assertEqual(project_members.count(), 1)

        payload = {
            'project': project.data.get('id'),
            'user': self.user2.id,
            'role': ProjectMembership.PROJECT_MANAGER
        }

        res = self.owner.post(ADD_MEMBER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        project_members = ProjectMembership.objects.filter(
            project_id=project.data.get('id'))

        self.assertEqual(project_members.count(), 2)

    def test_add_member_to_project_unauthorized(self):
        project_payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization.id
        }

        project = self.owner.post(LIST_CREATE_PROJECT_URL, project_payload)

        project_members = ProjectMembership.objects.filter(
            id=project.data.get('id'))

        self.assertEqual(project_members.count(), 1)

        payload = {
            'project': project.data.get('id'),
            'user': self.user2.id,
            'role': ProjectMembership.PROJECT_MANAGER
        }

        res = self.member.post(ADD_MEMBER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_member_to_project_successful(self):
        project_payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization.id
        }

        project = self.owner.post(LIST_CREATE_PROJECT_URL, project_payload)

        payload = {
            'project': project.data.get('id'),
            'user': self.user2.id,
            'role': ProjectMembership.PROJECT_MEMBER
        }

        self.owner.post(ADD_MEMBER_URL, payload)

        project_members = ProjectMembership.objects.filter(
            project_id=project.data.get('id'))

        self.assertEqual(project_members.count(), 2)

        payload = {'user': self.user2.id}

        res = self.owner.delete(REMOVE_MEMBER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        project_members = ProjectMembership.objects.filter(
            project_id=project.data.get('id'))

        self.assertEqual(project_members.count(), 1)

    def test_remove_member_to_project_unauthorized(self):
        project_payload = {
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization.id
        }

        project = self.owner.post(LIST_CREATE_PROJECT_URL, project_payload)

        payload = {
            'project': project.data.get('id'),
            'user': self.user2.id,
            'role': ProjectMembership.PROJECT_MANAGER
        }

        res = self.owner.post(ADD_MEMBER_URL, payload)

        project_members = ProjectMembership.objects.filter(
            project_id=project.data.get('id'))

        self.assertEqual(project_members.count(), 2)

        payload = {'user': self.user2.id}

        res = self.owner3.delete(REMOVE_MEMBER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
