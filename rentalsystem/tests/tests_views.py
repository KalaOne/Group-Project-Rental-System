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
    # item_listings?query_name=Where%27s%20Wally%3F%21

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
        self.assertIsNotNone(response.context['on_time_jobs_count'])
        self.assertIsNotNone(response.context['unallocated_jobs_count'])

        # if no post request is sent, jobstats should return 'All Regions'
        self.assertEqual(response.context['searched_region'], 'All')


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


class UtilityTests(TestCase):

    # test function returns None when called with nothing
    def test_get_lowest_prices(self):
        # test list returned is empty when no items passed in
        lowest_price = getLowestPrices()
        print("lowest_price = ", lowest_price)
        self.assertEqual(lowest_price, [])

 
class PostItemTests(TestCase):
#if page loads, test should pass
    def test_postitem_returns_correct_status(self):
        url = reverse('user_post_item')
        response = self.client.get(url) 
        self.assertEqual(response.status_code, 200)


#if correct tempate is loaded, pass
    def test_postitem_returns_correct_template(self):
        response = self.client.get('postItem/')
        self.assertTemplateUsed('user_post_item.html')


#if content of 'context' is not None, should pass
    # def test_form_fields_are_valid(self):
    #     url = reverse('item_details')
    #     response = self.client.post(url, {'dropdown_value' : 3 , 'info_field' : "Superb", 'Cost': 3})
    #     self.assertIsNotNone(response.context['item_name'])
    #     self.assertIsNotNone(response.context['info'])
    #     self.assertIsNotNone(response.context['cost'])
    #     self.assertIsNotNone(response.context['i_id'])

#