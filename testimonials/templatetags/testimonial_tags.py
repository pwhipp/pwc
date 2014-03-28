from mezzanine import template

from testimonials.models import Testimonial

register = template.Library()


@register.as_tag
def random_testimonials(limit=5):
    """
    Put a randomly selected list of testimonials into the template context
    Usage::
        {% random_testimonials 5 as random_testimonials %}
    """
    testimonials = Testimonial.objects.order_by('?')
    return list(testimonials[:limit])