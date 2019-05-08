from django.test import TestCase
from django.http import HttpRequest
from django.test import SimpleTestCase
from django.urls import reverse

from rentalsystem.views import *


# check home view returns something

class HomePageTests(TestCase):

    def test_home_view_returns_right_status(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_view_returns_right_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_landing_page_returns_right_status(self):
        url = reverse('landing')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_landing_page_returns_right_template(self):
        url = reverse('landing')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'landing.html')

    # def test_landing_page_returns_right_search_results(self):
    #     response = self.client.get('/home_search')
    #     self.

class JobStatsTests(TestCase):
    def test_jobstats_returns_right_status(self):
        url = reverse('jobstats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_jobstats_returns_right_status_returns_right_template(self):
        url = reverse('jobstats')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'jobstats.html')


    # tests all the data that a default jobstats page returns
    def test_jobstats_no_post_returns_context_data(self):
        url = reverse('jobstats')
        response = self.client.get(url)
        self.assertIsNotNone(response.context['total_jobs_completed_count'])
        self.assertIsNotNone(response.context['total_jobs_comp_last_week'])

        # if no post request is sent, jobstats should return 'All Regions'
        self.assertEqual(response.context['searched_region'], 'All Regions')


    # test post request returns data
    def test_jobstats_post_returns_context_data(self):
        url = reverse('jobstats')

        # create post request passing a search for "Norfolk in"
        response = self.client.post(url, {'region': 'Norfolk'})

        # if post request sent, should return region in context
        self.assertEqual(response.context['searched_region'], 'Norfolk')

class MyOrdersTests(TestCase):

    def test_myorders_returns_correctly(self):
        url = reverse('my_orders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'myorders.html')
