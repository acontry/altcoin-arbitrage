import parse_captcha
import requests
import io
import sys
from PIL import Image


def login(email, password):
	s = requests.Session()
	r = s.get('https://bter.com/captcha')
	i = Image.open(io.BytesIO(r.content))
	i.save('temp.png')

	captcha = parse_captcha.parse_captcha('temp.png')
	print('Captcha: ' + captcha)

	params = {'email':'email', 'password': 'pass', 'captcha': captcha, 'submit': 'Submit'}

	r = s.post('https://bter.com/login', params = params)
	#print(r.content)

if __name__ == '__main__':
	email = sys.argv[1]
	password = sys.argv[2]
	login(email, password)
