import re

from django import template as dt
from mezzanine import template
from mezzanine.blog.models import BlogPost
from django.contrib.contenttypes.models import ContentType

from hitcount.models import HitCount

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
    return [_find_blog_post(title_part) for title_part in title_parts]


class HitNode(dt.Node):
    def __init__(self, blog_post_vname, var_name=None):
        self.blog_post_var = dt.Variable(blog_post_vname)
        self.var_name = var_name

    def render(self, context):
        try:
            blog_post = self.blog_post_var.resolve(context)
        except dt.VariableDoesNotExist:
            return ''

        context[self.var_name] = self.get_hits(blog_post)

        return ''

    @staticmethod
    def get_hits(blog_post):
        try:
            content_type = ContentType.objects.get_for_model(blog_post)
            hitcount = HitCount.objects.get(content_type=content_type,
                                            object_pk=blog_post.pk)
            return hitcount.hits
        except HitCount.DoesNotExist:
            return 0


def blog_post_hits(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, args = token.contents.split(None, 1)
    except ValueError:
        raise dt.TemplateSyntaxError("{0} tag requires arguments".format(token.contents.split()[0]))
    m = re.search('(\w+) as (\w+)', args)
    if not m:
        raise dt.TemplateSyntaxError("{0} tag has invalid arguments".format(token.contents.split()[0]))
    blog_post_vname, var_name = m.groups()
    return HitNode(blog_post_vname, var_name)

register.tag('blog_post_hits', blog_post_hits)