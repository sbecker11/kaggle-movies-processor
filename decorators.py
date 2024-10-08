
from functools import wraps
from string_utils import SpecialChars

space_encoded = SpecialChars.PSI_CHAR.value

def space_decoder(target_func):
    @wraps(target_func)
    def wrapper(*args, **kwargs):
        # Call the original function
        result = target_func(*args, **kwargs)
        
        # Ensure result is a string before replacing
        if isinstance(result, str):
            # Perform post-processing
            result = result.replace(space_encoded, ' ')
        
        return result
    
    return wrapper