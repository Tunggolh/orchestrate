"""
Test cases for the organizations app.
"""

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from organizations.models import Organization, Membership
from organizations.serializers import OrganizationSerializer
from users.tests import create_user

LIST_CREATE_ORGANIZATION_URL = reverse('organizations:list_create')
DETAIL_ORGANIZATION_URL = reverse('organizations:detail', kwargs={'pk': 1})
ADD_MEMBER_URL = reverse('organizations:add_member', kwargs={'pk': 1})
REMOVE_MEMBER_URL = reverse('organizations:remove_member', kwargs={'pk': 1})


def create_organization(**params):
    return Organization.objects.create(**params)


def create_membership(**params):
    return Membership.objects.create(**params)


class OrganizationModelTests(TestCase):
    def test_create_organization_successful(self):
        name = 'Test Organization'
        domain = 'test.com'
        organization = Organization.objects.create(
            name=name,
            domain=domain
        )

        self.assertEqual(organization.name, name)
        self.assertEqual(organization.domain, domain)


class MembershipModelTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )

    def test_create_membership_successful(self):
        organization = create_organization(
            name='Test Organization',
            domain='test.com'
        )

        member = Membership.objects.create(
            user=self.user,
            organization=organization,
            role=Membership.ROLE_OWNER
        )

        self.assertEqual(member.user, self.user)
        self.assertEqual(member.organization, organization)
        self.assertEqual(member.role, Membership.ROLE_OWNER)


class PrivateOrganizationApiTests(TestCase):
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )
        self.client = APIClient()
        self.unauthenticated_client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_organizations_successful(self):
        organization1 = create_organization(
            name='Test Organization 1', domain='test1.com')
        organization2 = create_organization(
            name='Test Organization 2', domain='test2.com')

        create_membership(
            user=self.user,
            organization=organization1,
            role=Membership.ROLE_OWNER
        )

        create_membership(
            user=self.user,
            organization=organization2,
            role=Membership.ROLE_OWNER
        )

        organizations = [organization1, organization2]

        res = self.client.get(LIST_CREATE_ORGANIZATION_URL)

        organizations = Organization.objects.filter(
            memberships__user=self.user)
        serializer = OrganizationSerializer(organizations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_organization_successful(self):
        payload = {
            'name': 'Test Organization',
            'domain': 'test.com'
        }

        organization = self.client.post(LIST_CREATE_ORGANIZATION_URL, payload)

        organization_detail = self.client.get(DETAIL_ORGANIZATION_URL)

        self.assertEqual(organization_detail.data['name'], payload['name'])
        self.assertEqual(organization_detail.status_code, status.HTTP_200_OK)

    def test_retrieve_organizations_unauthorized(self):
        res = self.unauthenticated_client.get(LIST_CREATE_ORGANIZATION_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_organization_successful(self):
        payload = {
            'name': 'Test Organization',
            'domain': 'test.com'
        }

        self.client.post(LIST_CREATE_ORGANIZATION_URL, payload)

        payload = {
            'name': 'Updated Test Organization',
            'domain': 'updated.com'
        }

        res = self.client.patch(
            DETAIL_ORGANIZATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], payload['name'])
        self.assertEqual(res.data['domain'], payload['domain'])

    def test_create_organization_membership_successful(self):
        payload = {
            'name': 'Test Organization',
            'domain': 'test.com'
        }

        res = self.client.post(LIST_CREATE_ORGANIZATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        organization = Organization.objects.get(**res.data)
        self.assertEqual(organization.name, payload['name'])
        self.assertEqual(organization.domain, payload['domain'])

        membership = Membership.objects.get(
            user=self.user, organization=organization)

        self.assertEqual(membership.role, Membership.ROLE_OWNER)
        self.assertEqual(membership.user, self.user)

    def test_add_member_to_organization_successful(self):
        payload = {
            'name': 'Test Organization',
            'domain': 'test.com'
        }

        user = create_user(
            email='test2@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )

        res = self.client.post(LIST_CREATE_ORGANIZATION_URL, payload)

        organization = Organization.objects.get(domain=payload['domain'])

        payload = {
            'user': user.id,
            'role': Membership.ROLE_MEMBER
        }

        res = self.client.post(ADD_MEMBER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        members = Membership.objects.filter(organization=organization)

        self.assertEqual(members.count(), 2)

    def test_add_member_to_organization_unauthorized(self):
        payload = {
            'name': 'Test Organization',
            'domain': 'test.com'
        }

        user1 = create_user(
            email='test1@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )

        self.client.post(LIST_CREATE_ORGANIZATION_URL, payload)

        res = self.unauthenticated_client.post(ADD_MEMBER_URL, {
            'user': user1.id,
            'role': Membership.ROLE_MEMBER
        })

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        user2 = create_user(
            email='test2@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )

        new_client = APIClient()
        new_client.force_authenticate(user1)

        res = new_client.post(ADD_MEMBER_URL, {
            'user': user2.id,
            'role': Membership.ROLE_OWNER
        })

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_member_from_organization_successful(self):
        payload = {
            'name': 'Test Organization',
            'domain': 'test.com'
        }

        user1 = create_user(
            email='test1@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )

        self.client.post(LIST_CREATE_ORGANIZATION_URL, payload)
        self.client.post(ADD_MEMBER_URL, {
            'user': user1.id,
            'role': Membership.ROLE_MEMBER
        })

        payload = {
            'user': user1.id,
        }

        res = self.client.delete(REMOVE_MEMBER_URL, payload)

        members = Membership.objects.filter(organization_id=1)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(members.count(), 1)

    def test_remove_member_from_organization_unauthorized(self):
        payload = {
            'name': 'Test Organization',
            'domain': 'test.com'
        }

        user1 = create_user(
            email='test1@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )

        user2 = create_user(
            email='test2@example.com',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )

        self.client.post(LIST_CREATE_ORGANIZATION_URL, payload)
        self.client.post(ADD_MEMBER_URL, {
            'user': user1.id,
            'role': Membership.ROLE_MEMBER
        })
        self.client.post(ADD_MEMBER_URL, {
            'user': user2.id,
            'role': Membership.ROLE_MEMBER
        })

        res = self.unauthenticated_client.post(REMOVE_MEMBER_URL, {
            'user': user1.id,
            'organization': 1
        })

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        new_client = APIClient()
        new_client.force_authenticate(user1)

        payload = {
            'user': user2.id,
        }

        res = new_client.delete(REMOVE_MEMBER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
