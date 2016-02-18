#!/bin/env python3

import unittest

import config
from app import app

class FlaskTest(unittest.TestCase):

    def setUp(self):
        self.myapp = app.test_client()

    def test_wells(self):
        resp = self.myapp.get('/wells?wellid=&welltype=Oil&uwi=')
        html = resp.data.decode()        
        self.assertIn('3000', html)        

    def test_wrong_well(self):
        resp = self.myapp.get('/wells?wellid=&welltype=Tar&uwi=', follow_redirects=True)
        html = resp.data.decode()        
        self.assertIn('No matching wells found', html)         

    def test_well(self):
        resp = self.myapp.get('/well/1')
        html = resp.data.decode()
        self.assertIn('SKWI111062705025W300', html)

    def test_single_well_redirect(self):
        resp = self.myapp.get('/wells?wellid=7&welltype=&uwi=', follow_redirects=True)
        html = resp.data.decode()
        self.assertIn('SKWI111062705025W300', html)        

    def test_lease(self):
        resp = self.myapp.get('/lease/OL-0004')
        html = resp.data.decode()        
        self.assertIn('OL-0004', html)    

    def test_leases(self):
        resp = self.myapp.get('/leases')
        html = resp.data.decode()        
        self.assertIn('OL-0007', html)             

    def test_adriennews(self):
        resp = self.myapp.get('/adriennews?WellId=1')
        html = resp.data.decode()        
        self.assertIn('27.11', html)   
          

if __name__ == '__main__':
    unittest.main()