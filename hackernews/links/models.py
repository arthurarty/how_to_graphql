from django.db import models
from django.conf import settings


class Link(models.Model):
    url = models.URLField()
    description = models.TextField(blank=True)
    post_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.url


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    link = models.ForeignKey(
        'links.Link', related_name='votes', on_delete=models.CASCADE)
