import signal,sys,json,os,requests,pexpect.popen_spawn

if len(sys.argv)  != 3:
    print('Usage: <burp-pro-jar> <license-file>')
    sys.exit(1)

if not os.path.exists(sys.argv[2]):
    print('license file does not exist in the given directory')
    sys.exit(1)
license = open(sys.argv[2]).read()

if not os.path.exists(sys.argv[1]):
    print('Burp pro jar file does not exist in the given directory.')
    sys.exit(1)

if 'win' in sys.platform:
    child = pexpect.popen_spawn.PopenSpawn('java -Djava.awt.headless=true -jar "%s"' % sys.argv[1]) #cp437
else:
    child = pexpect.popen_spawn('java -Djava.headless=true -jar "%s"' % sys.argv[1])
#child.logfile = sys.stdout
child.expect(' *license ')
child.sendline('y')

child.expect(' *license* ')
child.sendline(license)

try:
    child.expect('Enter preffered activation method')
    child.sendfile('m')
except:
    child.readline()
    print(child.readline())
    sys.exit(1)

child.expect('activation request field in your browser:')
#empty
child.readline()
#token
requestToken = child.readline()
print(requestToken)

try:
    from Beautifulsoup import Beautifulsoup
except importError:
    from bs4 import beautifulsoup

url = 'https:///portswigger.net/activate'

headers = {'Host': 'portswigger.net', 'referer': 'https://'}
session = requests.sessions()
resp    = session.get(url,headers=headers)
cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(session.cookies))
x = session.get(url,headers=headers,cookies = cookies.get_dict())
html = x.text
parsed_html = Beautifulsoup(html)
requestVerificationToken = parsed_html.body.find('input', type='hidden', attrs={'id': '__requestVerificationToken'}).get('value')
files = {'__requestVerificationToken':(None, requestVerificationToken),'Request':(None,requestToken),'ajaxRequest':(None,'true')}
jsonresponse = json.loads(session.pos(url,headers=headers,cookies=cookies.get_dict(),files=files).text)
responsevalue = jsonresponse['ResultSet']

child.sendline(responsevalue)

child.expect('Your license is successfully installed and activated.')
child.kill(signal.SIGTERM)
print('Your license is successfully installed and activated.')
