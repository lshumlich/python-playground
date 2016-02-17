
import unittest

import config
import app

class our_flask_test(unittest.TestCase):

    def test_play_with_stuff(self):
        myapp = app.app.test_client()
#         resp = myapp.get('/wells')
        resp = myapp.get('/well/1')
#         resp = myapp.get('/adriennews/1')
        html = resp.data.decode('ascii')
        
        print(html)
        
        f = open(config.get_temp_dir() + 'teststuff.html','w')
        f.write(html)
        f.flush()
        f.close()
        
        
        
#         
#         print(resp)
#         print(resp.data)
#         print(resp.get_data())
#         print(resp.headers)
#         print(resp.status)
#         print(resp.mimetype)
        
        #
        # This is only so we can use the browser to see the html
        #

if __name__ == '__main__':
    unittest.main()