
from functools import wraps

# Usage:
# Example usage of char_decoder
# CHAR_ENCODED = SpecialChars.PSI_CHAR
# CHAR_UNCODED = ' '
# @char_decoder(SCHAR_ENCODEDR, CHAR_UNCODED)
# def example_function(args,vargs):
#     return output_string

# somewhere else in the code before calling
# the decorated function replace 
# define and use the dual function 
# of char_decoder:
#
# def char_encoder(input): 
#   return input.replace(CHAR_UNCODED, CHAR_ENCODED)
#
def char_decoder(encoded_char, uncoded_char):
    def decorator(target_func):
        @wraps(target_func)
        def wrapper(*args, **kwargs):
            # Call the original function with all positional and keyword arguments
            result = target_func(*args, **kwargs)
            
            # Ensure result is a string before replacing
            if isinstance(result, str):
                # Perform post-processing
                result = result.replace(encoded_char, uncoded_char)
            
            return result
        
        return wrapper
    
    return decorator
