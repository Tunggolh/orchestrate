from django.test import TestCase

from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from organizations.models import Membership
from organizations.tests import create_organization, create_membership

from projects.models import ProjectMembership
from projects.tests import create_projects, create_project_membership

from tasks.models import Task

from tasks.tests.test_columns import create_column
from users.tests import create_user

LIST_CREATE_TASKS_URL = reverse('tasks:list_create')
DETAIL_UPDATE_DELETE_TASK_URL = reverse('tasks:task_detail', kwargs={'pk': 1})


def create_task(**params):
    return Task.objects.create(**params)


class TaskModelTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user({
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe'
        })

        self.organization = create_organization({
            'name': 'Test Organization',
            'domain': 'testorg.com',
        })

        self.organization_membership = create_membership({
            'organization': self.organization,
            'user': self.user,
            'role': Membership.ORGANIZATION_OWNER
        })

        self.project = create_projects({
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization
        })

        self.project_membership = create_project_membership({
            'project': self.project,
            'user': self.user,
            'role': ProjectMembership.PROJECT_MANAGER
        })

        self.todo_column = create_column({
            'project': self.project,
            'name': 'To Do',
            'position': 1
        })

        self.done_column = create_column({
            'project': self.project,
            'name': 'Done',
            'position': 2
        })

    def test_create_task_successful(self):
        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.todo_column,
            'project': self.project,
            'assignee': self.user
        }

        task = create_task(data)

        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.description, 'Test Description')
        self.assertEqual(str(task.due_date), '2021-12-12 12:00:00')
        self.assertEqual(task.columns, self.todo_column)
        self.assertEqual(task.project, self.project)
        self.assertEqual(task.assignee, self.user)

        data2 = {
            'title': 'Test Task 2',
            'description': 'Test Description 2',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.done_column,
            'project': self.project,
            'assignee': self.user
        }

        task2 = create_task(data2)

        self.assertEqual(task2.title, 'Test Task 2')
        self.assertEqual(task2.description, 'Test Description 2')
        self.assertEqual(str(task2.due_date), '2021-12-12 12:00:00')
        self.assertEqual(task2.columns, self.done_column)
        self.assertEqual(task2.project, self.project)
        self.assertEqual(task2.assignee, self.user)

    def test_create_task_without_columns(self):
        with self.assertRaises(ValueError):
            create_task({
                'title': 'Test Task',
                'description': 'Test Description',
                'due_date': '2021-12-12 12:00:00',
                'project': self.project,
                'assignee': self.user
            })


class PublicTaskApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.user = create_user({
            'email': 'test@xample.com',
            'password': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe'
        })

        self.organization = create_organization({
            'name': 'Test Organization',
            'domain': 'testorg.com'
        })

        self.organization_membership = create_membership({
            'organization': self.organization,
            'user': self.user,
            'role': Membership.ORGANIZATION_OWNER
        })

        self.project = create_projects({
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization
        })

        self.project_membership = create_project_membership({
            'project': self.project,
            'user': self.user,
            'role': ProjectMembership.PROJECT_MANAGER
        })

    def test_list_tasks_unauthenticated(self):
        column = create_column({
            'project': self.project,
            'name': 'To Do',
            'position': 1
        })

        res = self.client.get(LIST_CREATE_TASKS_URL, {
            'project_id': self.project.id, 'column_id': column.id})

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_unauthenticated(self):
        self.column = create_column({
            'project': self.project,
            'name': 'To Do',
            'position': 1
        })

        res = self.client.post(LIST_CREATE_TASKS_URL, {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.column.id,
            'project': self.project.id,
            'assignee': self.user.id
        })

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTaskApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.user = create_user({
            'email': 'test@xample.com',
            'password': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe'
        })

        self.user_member = create_user({
            'email': 'test2@example.com',
            'password': 'testpass123',
            'first_name': 'Jane',
            'last_name': 'Doe'
        })

        self.user_external = create_user({
            'email': 'test3@example.com',
            'password': 'testpass123',
            'first_name': 'Juan',
            'last_name': 'Dela Cruz'
        })

        self.organization = create_organization({
            'name': 'Test Organization',
            'domain': 'testorg.com'
        })

        self.organization2 = create_organization({
            'name': 'Test Organization 2',
            'domain': 'testorg2.com'
        })

        self.organization_membership = create_membership({
            'organization': self.organization,
            'user': self.user,
            'role': Membership.ORGANIZATION_OWNER
        })

        self.organization_membership2 = create_membership({
            'organization': self.organization,
            'user': self.user_member,
            'role': Membership.ORGANIZATION_MEMBER
        })

        self.organization_membership3 = create_membership({
            'organization': self.organization2,
            'user': self.user_external,
            'role': Membership.ORGANIZATION_OWNER
        })

        self.project = create_projects({
            'name': 'Test Project',
            'description': 'Test Description',
            'organization': self.organization
        })

        self.project_membership = create_project_membership({
            'project': self.project,
            'user': self.user,
            'role': ProjectMembership.PROJECT_MANAGER
        })

        self.project_membership2 = create_project_membership({
            'project': self.project,
            'user': self.user_member,
            'role': ProjectMembership.PROJECT_MEMBER
        })

        self.column = create_column({
            'project': self.project,
            'name': 'To Do',
            'position': 1
        })

        self.manager.force_authenticate(user=self.user)
        self.member.force_authenticate(user=self.user_member)
        self.external.force_authenticate(user=self.user_external)

    def test_create_task_successful(self):
        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.column.id,
            'project': self.project.id,
            'assignee': self.member.id
        }

        self.manager.post(LIST_CREATE_TASKS_URL, data)

        res = self.manager.get(LIST_CREATE_TASKS_URL, {
            'project_id': self.project.id, 'column_id': self.column.id})

        self.assertEqual(len(res.data), 1)

        res = self.member.get(LIST_CREATE_TASKS_URL, {
            'project_id': self.project.id})

        self.assertEqual(len(res.data), 1)

    def test_create_task_unauthorized(self):
        """ Only project members can create tasks """
        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.column.id,
            'project': self.project.id,
            'assignee': self.member.id
        }

        res = self.external.post(LIST_CREATE_TASKS_URL, data)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_task_assignee_not_a_member(self):
        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.column.id,
            'project': self.project.id,
            'assignee': self.external.id
        }

        res = self.manager.post(LIST_CREATE_TASKS_URL, data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_tasks_successful(self):
        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.column.id,
            'project': self.project.id,
            'assignee': self.member.id
        }

        create_task(data)

        res = self.manager.get(LIST_CREATE_TASKS_URL, {
            'project_id': self.project.id})

        self.assertEqual(len(res.data), 1)

        res = self.member.get(LIST_CREATE_TASKS_URL, {
            'project_id': self.project.id})

        self.assertEqual(len(res.data), 1)

    def test_list_tasks_assigned_to_user(self):
        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.column.id,
            'project': self.project.id,
            'assignee': self.member.id
        }

        create_task(data)

        res = self.manager.get(LIST_CREATE_TASKS_URL, {
            'project_id': self.project.id, 'assignee': self.member.id})

        self.assertEqual(len(res.data), 1)

        res = self.member.get(LIST_CREATE_TASKS_URL, {
            'project_id': self.project.id, 'assignee': self.manager.id})

        self.assertEqual(len(res.data), 0)

    def test_list_tasks_unauthorized(self):
        """ Only project members can list tasks """
        res = self.external.get(LIST_CREATE_TASKS_URL, {
            'project_id': self.project.id})

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_task_successful(self):
        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.column.id,
            'project': self.project.id,
            'assignee': self.member.id
        }

        create_task(data)

        data = {
            'title': 'Test Task Updated',
            'description': 'Test Description Updated',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.column.id,
            'project': self.project.id,
            'assignee': self.member.id
        }

        res = self.manager.patch(
            DETAIL_UPDATE_DELETE_TASK_URL, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_task_unauthorized(self):
        """ Only project members can update tasks """
        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.column.id,
            'project': self.project.id,
            'assignee': self.member.id
        }

        create_task(data)

        data = {
            'title': 'Test Task Updated',
            'description': 'Test Description Updated',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.column.id,
            'project': self.project.id,
            'assignee': self.member.id
        }

        res = self.external.patch(
            DETAIL_UPDATE_DELETE_TASK_URL, data)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_task_successful(self):
        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.column.id,
            'project': self.project.id,
            'assignee': self.member.id
        }

        create_task(data)

        res = self.manager.delete(DETAIL_UPDATE_DELETE_TASK_URL)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_task_unauthorized(self):
        """ Only project manager can delete tasks """
        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'due_date': '2021-12-12 12:00:00',
            'columns': self.column.id,
            'project': self.project.id,
            'assignee': self.member.id
        }

        create_task(data)

        res_member = self.member.delete(DETAIL_UPDATE_DELETE_TASK_URL)
        res_external = self.external.delete(DETAIL_UPDATE_DELETE_TASK_URL)

        self.assertEqual(res_member.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res_external.status_code, status.HTTP_403_FORBIDDEN)
