import requests
from my_package import hello_world
import my_package_b

r = requests.get("https://google.com")
print(r.status_code)

hello_world()
my_package_b.hello_world()
