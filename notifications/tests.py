import json

from django.test import TestCase
from models import Notification


# Create your tests here.
print(json.dumps(Notification(["test"], "test", "aaa", "test")))
