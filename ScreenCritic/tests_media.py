import os
import importlib
from django.urls import reverse
from django.test import TestCase
from django.conf import settings

FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}TwD TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"

class MoviePageTests(TestCase):
    def setUp(self):
        self.views_module = importlib.import_module('ScreenCritic.views')
        self.views_module_listing = dir(self.views_module)
        
        self.project_urls_module = importlib.import_module('WAD2_TEAM5A_PROJECT.urls')

    def test_view_exists(self):
        """
        Does the index() view exist in Rango's views.py module?
        """
        name_exists = 'movie_list' in self.views_module_listing
        is_callable = callable(self.views_module.movie_list)
        
        self.assertTrue(name_exists, f"{FAILURE_HEADER}The movie_list() view for rango does not exist.{FAILURE_FOOTER}")
        self.assertTrue(is_callable, f"{FAILURE_HEADER}Check that you have created the movie_list() view correctly. It doesn't seem to be a function!{FAILURE_FOOTER}")
    
        