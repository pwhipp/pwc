from django.contrib import admin
from mezzanine.blog.admin import BlogPostAdmin
from mezzanine.blog.models import BlogPost
from django.contrib.contenttypes.models import ContentType

from hitcount.models import HitCount


class MyBlogPostAdmin(BlogPostAdmin):
    list_display = ["title", "user", "status", "hits", "admin_link"]

    @staticmethod
    def hits(blog_post):
        try:
            content_type = ContentType.objects.get_for_model(blog_post)
            hitcount = HitCount.objects.get(content_type=content_type,
                                            object_pk=blog_post.pk)
            return hitcount.hits
        except HitCount.DoesNotExist:
            return 0

admin.site.unregister(BlogPost)
admin.site.register(BlogPost, MyBlogPostAdmin)
