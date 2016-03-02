
class Utils(object):
    
    def obj_to_dict(self,obj,dic = None):
        """ 
        This will append or create a dictionary object with property attributes of an object
        The dictionary object is returned for convenience. 
        """
        if dic == None:
            dic = dict()
        for attr in obj.__dict__:
            if not attr.startswith('_'):
                dic[attr] =obj. __dict__[attr]
        return dic
