from horseman.validation import Validator
from horseman.response import reply


basic_user_schema = {
    'username': str
}

complex_user_schema = {
    'username': str,
    'email': str
}


def test_simple_validation():
    validator = Validator(basic_user_schema)
    validator.validate_object({'username': 1})
    

def test_complex_validation():
    validator = Validator(complex_user_schema)
    validator.validate_object({'username': 1})
    
