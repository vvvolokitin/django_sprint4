class UsernamePathConverter:
    regex = '[a-zA-Z0-9_.-@+]{1,150}'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
