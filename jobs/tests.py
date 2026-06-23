from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Job, Application

User = get_user_model()


class JobTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.employer = User.objects.create_user(
            username='testemployer',
            email='employer@test.com',
            password='testpass123',
            role='employer',
        )
        self.employer2 = User.objects.create_user(
            username='testemployer2',
            email='employer2@test.com',
            password='testpass123',
            role='employer',
        )
        self.candidate = User.objects.create_user(
            username='testcandidate',
            email='candidate@test.com',
            password='testpass123',
            role='candidate',
        )

        self.job = Job.objects.create(
            employer=self.employer,
            title='Backend Engineer',
            description='Django experience required.',
            location='Kathmandu',
            salary_min=50000,
            salary_max=80000,
            status='open',
        )

    def get_token(self, username, password='testpass123'):
        response = self.client.post('/api/accounts/login/', {
            'username': username,
            'password': password,
        }, format='json')
        return response.data['access']

    def authenticate(self, username):
        token = self.get_token(username)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # --- Public access tests ---
    def test_list_jobs_is_public(self):
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_job_is_public(self):
        response = self.client.get(f'/api/jobs/{self.job.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Backend Engineer')

    # --- Employer job creation ---
    def test_employer_can_create_job(self):
        self.authenticate('testemployer')
        response = self.client.post('/api/jobs/', {
            'title': 'Senior Engineer',
            'description': 'Senior level position.',
            'location': 'Lalitpur',
            'salary_min': 80000,
            'salary_max': 120000,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['employer']['username'], 'testemployer')

    def test_candidate_cannot_create_job(self):
        self.authenticate('testcandidate')
        response = self.client.post('/api/jobs/', {
            'title': 'Candidate Job',
            'description': 'Should not be allowed.',
            'location': 'Kathmandu',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_create_job(self):
        response = self.client.post('/api/jobs/', {
            'title': 'No Auth Job',
            'description': 'Should not be allowed.',
            'location': 'Kathmandu',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Ownership enforcement ---
    def test_employer_can_update_own_job(self):
        self.authenticate('testemployer')
        response = self.client.put(f'/api/jobs/{self.job.pk}/', {
            'title': 'Updated Title',
            'description': 'Updated description.',
            'location': 'Kathmandu',
            'salary_min': 55000,
            'salary_max': 85000,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_employer_cannot_update_another_employers_job(self):
        self.authenticate('testemployer2')
        response = self.client.put(f'/api/jobs/{self.job.pk}/', {
            'title': 'Stolen Update',
            'description': 'Should fail.',
            'location': 'Kathmandu',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employer_can_delete_own_job(self):
        self.authenticate('testemployer')
        response = self.client.delete(f'/api/jobs/{self.job.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Job.objects.filter(pk=self.job.pk).exists())

    def test_employer_cannot_delete_another_employers_job(self):
        self.authenticate('testemployer2')
        response = self.client.delete(f'/api/jobs/{self.job.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Job.objects.filter(pk=self.job.pk).exists())

    # --- Filtering ---
    def test_filter_jobs_by_location(self):
        Job.objects.create(
            employer=self.employer,
            title='Remote Job',
            description='Remote position.',
            location='Lalitpur',
            status='open',
        )
        response = self.client.get('/api/jobs/?location=kathmandu')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        for job in results:
            self.assertIn('kathmandu', job['location'].lower())

    def test_search_jobs_by_title(self):
        response = self.client.get('/api/jobs/?search=backend')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(len(results) >= 1)
        self.assertTrue(any('backend' in job['title'].lower() for job in results))

    def test_paginated_response_structure(self):
        response = self.client.get('/api/jobs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)


class ApplicationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.employer = User.objects.create_user(
            username='testemployer',
            email='employer@test.com',
            password='testpass123',
            role='employer',
        )
        self.candidate = User.objects.create_user(
            username='testcandidate',
            email='candidate@test.com',
            password='testpass123',
            role='candidate',
        )
        self.candidate2 = User.objects.create_user(
            username='testcandidate2',
            email='candidate2@test.com',
            password='testpass123',
            role='candidate',
        )

        self.job = Job.objects.create(
            employer=self.employer,
            title='Backend Engineer',
            description='Django experience required.',
            location='Kathmandu',
            status='open',
        )

    def get_token(self, username, password='testpass123'):
        response = self.client.post('/api/accounts/login/', {
            'username': username,
            'password': password,
        }, format='json')
        return response.data['access']

    def authenticate(self, username):
        token = self.get_token(username)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_candidate_can_apply_to_job(self):
        self.authenticate('testcandidate')
        response = self.client.post(f'/api/jobs/{self.job.pk}/apply/', {
            'cover_letter': 'I am a strong fit.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'applied')
        self.assertEqual(response.data['candidate']['username'], 'testcandidate')

    def test_candidate_cannot_apply_twice(self):
        self.authenticate('testcandidate')
        self.client.post(f'/api/jobs/{self.job.pk}/apply/', {
            'cover_letter': 'First application.',
        }, format='json')
        response = self.client.post(f'/api/jobs/{self.job.pk}/apply/', {
            'cover_letter': 'Second application.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_employer_cannot_apply_to_job(self):
        self.authenticate('testemployer')
        response = self.client.post(f'/api/jobs/{self.job.pk}/apply/', {
            'cover_letter': 'Employer applying.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_candidate_cannot_apply_to_closed_job(self):
        self.job.status = 'closed'
        self.job.save()
        self.authenticate('testcandidate')
        response = self.client.post(f'/api/jobs/{self.job.pk}/apply/', {
            'cover_letter': 'Applying to closed job.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_employer_sees_only_their_applications(self):
        Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            status='applied',
        )
        other_job = Job.objects.create(
            employer=self.candidate,
            title='Other Job',
            description='Other.',
            location='Lalitpur',
            status='open',
        )
        self.authenticate('testemployer')
        response = self.client.get('/api/jobs/applications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        for application in results:
            self.assertEqual(application['candidate']['username'], 'testcandidate')

    def test_candidate_sees_only_their_applications(self):
        Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            status='applied',
        )
        Application.objects.create(
            job=self.job,
            candidate=self.candidate2,
            status='applied',
        )
        self.authenticate('testcandidate')
        response = self.client.get('/api/jobs/applications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        for application in results:
            self.assertEqual(application['candidate']['username'], 'testcandidate')


class StatusTransitionTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.employer = User.objects.create_user(
            username='testemployer',
            email='employer@test.com',
            password='testpass123',
            role='employer',
        )
        self.candidate = User.objects.create_user(
            username='testcandidate',
            email='candidate@test.com',
            password='testpass123',
            role='candidate',
        )

        self.job = Job.objects.create(
            employer=self.employer,
            title='Backend Engineer',
            description='Django experience required.',
            location='Kathmandu',
            status='open',
        )
        self.application = Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            status='applied',
        )

    def get_token(self, username, password='testpass123'):
        response = self.client.post('/api/accounts/login/', {
            'username': username,
            'password': password,
        }, format='json')
        return response.data['access']

    def authenticate(self, username):
        token = self.get_token(username)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def patch_status(self, new_status):
        return self.client.patch(
            f'/api/jobs/applications/{self.application.pk}/status/',
            {'status': new_status},
            format='json',
        )

    def test_employer_can_move_applied_to_reviewed(self):
        self.authenticate('testemployer')
        response = self.patch_status('reviewed')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'reviewed')

    def test_employer_can_move_reviewed_to_accepted(self):
        self.application.status = 'reviewed'
        self.application.save()
        self.authenticate('testemployer')
        response = self.patch_status('accepted')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'accepted')

    def test_invalid_transition_applied_to_accepted(self):
        self.authenticate('testemployer')
        response = self.patch_status('accepted')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'applied')

    def test_invalid_transition_from_terminal_state(self):
        self.application.status = 'accepted'
        self.application.save()
        self.authenticate('testemployer')
        response = self.patch_status('reviewed')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'accepted')

    def test_candidate_cannot_update_status(self):
        self.authenticate('testcandidate')
        response = self.patch_status('reviewed')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'applied')

    def test_invalid_transition_returns_correct_error_message(self):
        self.authenticate('testemployer')
        response = self.patch_status('accepted')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_detail = str(response.data)
        self.assertIn('applied', error_detail)
        self.assertIn('accepted', error_detail)
