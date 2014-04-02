from mezzanine import template
from mezzanine.blog.models import BlogPost

register = template.Library()


def _find_blog_post(title_part):
    """
    Return the first blog matching title_part.
    Used to obtain a specific blog entry in a template e.g.
    {% find_blog_post "Why You Need Agile Development" as agile_post %}
    """
    try:
        return BlogPost.objects.filter(title__icontains=title_part)[0]
    except IndexError:  # nothing matched
        return None

@register.as_tag
def find_blog_post(title_part):
    """
    Return the first blog matching title_part.
    Used to obtain a specific blog entry in a template e.g.
    {% find_blog_post "Why You Need Agile Development" as agile_post %}
    """
    return _find_blog_post(title_part)


@register.as_tag
def find_blog_posts(*title_parts):
    """
    Return a list of blog entries - one for each matching title_part.
    Used to obtain a list of specific blog entries in a template e.g.
    {% find_blog_posts ["Why You Need Agile Development", "Why you need a beautiful site"] %}
    """
    print(title_parts)
    return [_find_blog_post(title_part) for title_part in title_parts]