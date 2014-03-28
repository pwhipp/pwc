from django.db import models
from django.core.urlresolvers import reverse

from mezzanine.core.models import Displayable, RichText
from mezzanine.conf import settings

from utils.email import send_email


class Testimonial(Displayable, RichText):
    """
    A testimonial someone has given.
    """
    author = models.TextField()

    def get_absolute_url(self):
        return reverse("testimonial", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        subject = "A new testimonial has been created on '{}'".format(settings.SITE_TITLE)
        for (name, email) in settings.MANAGERS:
            context = {'testimonial': self,
                       'name': name,
                       'site_title': settings.SITE_TITLE}
            send_email(subject, [email], 'testimonials/email/notification.html', context)
        return result