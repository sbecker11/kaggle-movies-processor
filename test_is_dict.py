from movie_column_types import extract_dict, is_dict

if __name__ == '__main__':

    case_1 = "{'id': 9068, 'name': 'The Prophecy Collection', 'poster_path': '/pU4wvBeirFDNk8rs9tsGZLa7Kyb.jpg', 'backdrop_path': None}"
    assert is_dict(case_1), "expected True but got False"
    
    expected_1 = {"id": 9068, "name": "The Prophecy Collection", "poster_path": "/pU4wvBeirFDNk8rs9tsGZLa7Kyb.jpg", "backdrop_path": None} 
    result_1 = extract_dict(case_1)
    assert result_1 == expected_1, f"expected {expected_1} but got {result_1}"

    print("PASSED")