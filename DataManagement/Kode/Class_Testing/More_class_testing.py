class User():
    def __init__(self, name, tag, password):
        self._name = name
        self._tag = tag
        self._password = password
        
    @property
    def name(self):
        return self._name
    
    @property
    def password(self):
        raise AttributeError('Password not readable.')
        
    @password.setter
    def password(self, new_password):
        self._password = new_password
        
    @property
    def tag(self):
        return self._tag
    
    @tag.setter
    def tag(self, new_tag):
        self._tag = new_tag