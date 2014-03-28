from django.db import models
from django.core.urlresolvers import reverse

from mezzanine.core.models import Displayable, RichText


class Testimonial(Displayable, RichText):
    """
    A testimonial someone has given.
    """
    author = models.TextField()

    def get_absolute_url(self):
        return reverse("testimonial", kwargs={"slug": self.slug})