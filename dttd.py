import sys
from requests import Session
from pyuseragents import random as random_useragent
from capmonster_python import RecaptchaV2Task, CapmonsterException
from json import loads
from msvcrt import getch
from os import system
from urllib3 import disable_warnings
from loguru import logger
from platform import system as platform_system
from platform import platform
from multiprocessing.dummy import Pool
from dotenv import dotenv_values
from random import randint, choice


disable_warnings()
def clear(): return system('cls' if platform_system() == "Windows" else 'clear')
logger.remove()
logger.add(sys.stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <cyan>{line}</cyan> - <white>{message}</white>")


if 'Windows' in platform():
	from ctypes import windll
	windll.kernel32.SetConsoleTitleW('DTTD Auto Reger | by NAZAVOD')

print('Telegram channel - https://t.me/n4z4v0d\n')

config = dotenv_values('env.txt')
ANTICAPTCHA_KEY = str(config['CAPTCHA_API_KEY'])

threads = int(input('Threads: '))
emails_directory = str(input('Drop .txt with emails: '))
use_proxy = str(input('Use Proxies? (y/N): ')).lower()

if use_proxy == 'y':
	proxy_source = int(input('How take proxies? (1 - tor proxies; 2 - from file): '))

	if proxy_source == 2:
		proxy_type = str(input('Enter proxy type (http; https; socks4; socks5): '))
		proxy_folder = str(input('Drag and drop file with proxies (ip:port; user:pass@ip:port): '))

with open(emails_directory, 'r') as file:
	emails_list = [row.strip() for row in file]

class Wrong_Response(BaseException):
	def __init__(self, message):
		self.message = message

def random_tor_proxy():
	proxy_auth = str(randint(1, 0x7fffffff)) + ':' + str(randint(1, 0x7fffffff))
	proxies = {'http': 'socks5://{}@localhost:9150'.format(proxy_auth), 'https': 'socks5://{}@localhost:9150'.format(proxy_auth)}
	return(proxies)

def take_random_proxy():
	with open(proxy_folder, 'r') as file:
		proxies = [row.strip() for row in file]

	return(choice(proxies))

def mainth(current_email):
	for _ in range(100):
		try:
			session = Session()
			session.headers.update({'user-agent': random_useragent(), 'Content-Type': 'application/json', 'X-Wix-Client-Artifact-Id': 'wix-form-builder', 'Referer': 'https://www.dttd.io/_partials/wix-thunderbolt/dist/clientWorker.cd194b3d.bundle.min.js'})

			if use_proxy == 'y':
				if proxy_source == 1:
					session.proxies.update(random_tor_proxy())

				else:
					proxy_str = take_random_proxy()
					session.proxies.update({'http': f'{proxy_type}://{proxy_str}', 'https': f'{proxy_type}://{proxy_str}'}
					)

			r = session.get('https://www.dttd.io/_api/v2/dynamicmodel')
			token = loads(r.text)['apps']['14ce1214-b278-a7e4-1373-00cebd1bef7c']['instance']

			session.headers.update({'Authorization': token})

			while True:
				try:
					logger.info(f'{current_email} | Trying to solve a captcha')
					capmonster = RecaptchaV2Task(ANTICAPTCHA_KEY)
					task_id = capmonster.create_task('https://www.dttd.io/', '6Ld0J8IcAAAAANyrnxzrRlX1xrrdXsOmsepUYosy')
					result = capmonster.join_task_result(task_id)
					captcha_response = result.get("gRecaptchaResponse")
				except CapmonsterException as err:
					logger.error(f'Error when solving captcha for {current_email}: {str(err.error_code)}, trying again')

				except Exception as error:
					logger.error(f'Error when solving captcha for {current_email}: {str(error)}, trying again')
				else:
					logger.success(f'Captcha successfully solved for {current_email}')
					break

			r = session.post('https://www.dttd.io/_api/wix-forms/v1/submit-form', json = {"formProperties":{"formName":"Subscriptions","formId":"comp-kyepzxc4"},"emailConfig":{"sendToOwnerAndEmails":{"emailIds":[]}},"viewMode":"Site","fields":[{"fieldId":"comp-kyepzxc92","label":"Enter Email Address","email":{"value":current_email,"tag":"main"}}],"labelKeys":["custom.subscriptions"],"security":{"captcha":captcha_response}})

			if not r.ok:
				raise Wrong_Response(r)
		
		except Exception as error:
			logger.error(f'{current_email} | Unexpected error : {str(error)}')

		except Wrong_Response as error:
			logger.error(f'{current_email} | Wrong response: {str(error)}, response code: {str(r.status_code)}, response: {str(r.text)}')

		else:
			with open('registered.txt', 'a') as file:
				file.write(f'{current_email}\n')

			logger.success(f'{current_email} | Successfully registered')

			return

	with open('unregistered.txt', 'a') as file:
		file.write(f'{current_email}\n')


if __name__ == '__main__':
	clear()
	pool = Pool(threads)
	result_list = pool.map(mainth, emails_list)
	logger.success('Работа успешно завершена!')
	print('\nPress Any Key To Exit..')
	getch()
	sys.exit()
