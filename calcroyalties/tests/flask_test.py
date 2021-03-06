#!/bin/env python3

import unittest
from flask import template_rendered
from contextlib import contextmanager
import src.app

app = src.app.app

class Test(unittest.TestCase):

    @contextmanager
    def captured_templates(self, app):
        recorded = []
        def record(sender, template, context, **extra):
            recorded.append((template, context))
        template_rendered.connect(record, app)
        try:
            yield recorded
        finally:
            template_rendered.disconnect(record, app)

    def test_leases_template(self):
        with self.captured_templates(app) as templates:
            rv = app.test_client().get('/leases/')
            # assert rv.status_code == 200
            # assert len(templates) == 1
            template, context = templates[0]
            with app.test_request_context():
                # print(template.render())
                assert 'Aliquam nunc sapien' in template.render()
                assert 'Hi, Larry!' not in template.render()

                print(template.render())

                print ("Templates:", templates[0])
            # assert template.name == 'index.html'
            # assert len(context['items']) == 10