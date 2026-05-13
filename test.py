# import json
# import jwt
# import requests



# URL = "http://localhost:5000/resend-otp"
# payload =  {
#     'email': 'flask3975@gmail.com'
# }

# response = requests.post(url=URL, data=json.dumps(payload))
# print(response.json())


# # token = jwt.encode(
# #     {"name": "Sean"}, "secret-key",
# #     algorithm="HS256"
# # )

# # print(token)




# # new_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30"
# # decoded_data = jwt.decode(
# #     new_token,
# #     key='a-string-secret-at-least-256-bits-long',
# #     algorithms=['HS256'])
# # print(decoded_data)









import unittest

def add(x, y):
    return x + y

class AddTestCase(unittest.TestCase):
    def test_add_function(self):
        self.assertEqual(add(2, 2), 4)

    def test_concatenation(self):
        self.assertEqual(add('ab', 'xy'), 'abxy')

    def test_add_function(self):
        self.assertNotEqual(add(10, 13), 5)


if __name__ == '__main__':
    unittest.main()