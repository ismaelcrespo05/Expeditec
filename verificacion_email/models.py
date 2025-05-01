from django.db import models

# Create your models here.
from django.contrib.auth.models import User

User.add_to_class('tocken', models.TextField(null=True))