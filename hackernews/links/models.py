from django.db import models


class Link(models.Model):
    url = models.URLField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.url
