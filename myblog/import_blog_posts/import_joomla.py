"""
Import the articles from joomla as blog_posts.
"""
from django.contrib.auth.models import User
from mezzanine.blog.models import BlogPost, BlogCategory
from mezzanine.generic.models import ThreadedComment
from django.contrib.contenttypes.models import ContentType

from hitcount.models import HitCount


class JoomlaImporter(object):

    def __init__(self, dry_run, verbosity):
        self.dry_run = dry_run
        self.verbosity = verbosity

    def vprint(self, msg, verbosity_level=0):
        """
        print if verbosity_level exceeds verbosity
        """
        if self.verbosity >= verbosity_level:
            print(msg)

    @staticmethod
    def get_or_create(model_class, **kwargs):
        """
        Return existing instance if there is one, otherwise create and return a new one.
        """
        # use code/user_group to get asset
        try:
            return model_class.objects.get(**kwargs)
        except model_class.DoesNotExist:
            return model_class(**kwargs)

    def import_articles(self, article_rows):
        self.vprint("BEGIN Importing articles", 1)
        blog_post_ctype = ContentType.objects.get_for_model(BlogPost)
        user = User.objects.get(username="paul")
        for row in article_rows:
            self.vprint("    Importing row: {}/{}/{}".format(row['section'], row['category'], row['title']), 2)
            if row['section'] == 'services':
                # Add it as a page
                self.vprint("Its a page: skipped for now", 3)
            else:
                # Add it as a blog entry
                blog_post = self.get_or_create(BlogPost, title=row['title'])
                blog_post.user = user

                blog_post.title = row['title']
                blog_post.content = row['introtext'] + row['fulltext']
                if not self.dry_run:
                    # Save it a first time so many to many category relation and hitcount can be set up
                    blog_post.save()

                    # Assign created/updated date (this must be done after the first save)
                    blog_post.created = row['created']
                    blog_post.updated = row['modified'] or row['created']
                    blog_post.publish_date = blog_post.updated

                    # Assign its hits
                    try:
                        hitcount = HitCount.objects.get(
                            content_type=blog_post_ctype,
                            object_pk=blog_post.pk)
                    except HitCount.DoesNotExist:
                        hitcount = HitCount(content_object=blog_post)
                    hitcount.hits = row['hits']
                    hitcount.save()

                    # Assign it a category
                    category_title = self.get_blog_post_category_title(row)
                    if category_title is not None:
                        category = BlogCategory.objects.get(title=category_title)
                        blog_post.categories.add(category)

                    # Save it a second time to ensure the category and created dates are saved too
                    blog_post.save()

                    # Assign its comments
                    for comment_row in row['comments']:
                        comment = self.get_or_create(ThreadedComment,
                                                     user_name=comment_row['name'],
                                                     comment=comment_row['comment'])
                        comment.content_object = blog_post
                        comment.user_name = comment_row['name']

                        comment_content = comment_row['title']
                        if len(comment_content) > 0:
                            comment_content += "\n"
                        comment_content += comment_row['comment']

                        comment.comment = comment_content
                        comment.user_email = comment_row['email']
                        comment.user_url = comment_row['website']
                        comment.submit_date = comment_row['date']
                        comment.ip_address = comment_row['ip']
                        comment.save()

        self.vprint("END   Importing articles", 1)

    @staticmethod
    def get_blog_post_category_title(article_row):
        """
        Return a category (name) to use for the article_row being imported.
        """
        try:
            return {"Whippy's theories": "Whippy's Theories",
                    "Web development": "Web Development"}[article_row['category']]
        except KeyError:
            return None


def dictfetchall(cursor):
    """
    Returns all rows from a cursor as a dict
    """
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()]


def get_cursor(db_name, db_username, db_userpassword):
    """
    Return a cursor to use with the specified database.
    """
    from django.db import ConnectionHandler

    source_databases = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': db_name,
            'USER': db_username,
            'PASSWORD': db_userpassword,
            'HOST': '',
            'PORT': ''}}
    return ConnectionHandler(source_databases)['default'].cursor()


def get_article_comments(db_name, db_username, db_userpassword, article_row):
    """
    Return a full list of the comments associated with the article_row, sorted by date.
    """
    qry = """
SELECT
    *
FROM
    jos_jomcomment
WHERE
    contentid = {} AND
    published = 1
ORDER BY date""".format(article_row['id'])

    cursor = get_cursor(db_name, db_username, db_userpassword)
    cursor.execute(qry)
    return dictfetchall(cursor)


def get_article_rows(db_name, db_username, db_userpassword):
    """
    Return a full list of the articles as dict rows for further processing.
    This assumes there are not too many (<5,000).
    """
    qry = """
SELECT
    content.*,
    section.title AS 'section',
    category.title AS 'category'
FROM
    jos_content AS content
    JOIN jos_sections AS section ON content.sectionid = section.id
    JOIN jos_categories AS category ON content.catid = category.id
WHERE
    state > 0 AND
    section.alias NOT IN ("testimonials")"""
    cursor = get_cursor(db_name, db_username, db_userpassword)
    cursor.execute(qry)
    article_rows = dictfetchall(cursor)
    for article_row in article_rows:
        article_row['comments'] = get_article_comments(db_name,
                                                       db_username,
                                                       db_userpassword,
                                                       article_row)
    return article_rows


def process_command_line(importer_class):
    """
    Process the command line, passing the csv files and parameters to the importer_class
    """
    import argparse

    parser = argparse.ArgumentParser(description="Import Joomla articles as blog posts.")
    parser.add_argument('db_name', help='name of the local mysql database being used for the import')
    parser.add_argument('db_username', help='username to access the local mysql database')
    parser.add_argument('db_userpassword', help='user password to access the local mysql database')
    parser.add_argument('--dry_run', '--dry', default=False, action='store_true',
                        help='run through without actually importing (defaults to false)')
    parser.add_argument('--verbosity', '--v', type=int, choices=[0, 1, 2, 3], default=1,
                        help='controls the amount of information printed \
                        0: nothing, 1: just table (default), 2: row, 3: field')
    args = parser.parse_args()

    importer = importer_class(args.dry_run, args.verbosity)
    importer.import_articles(get_article_rows(args.db_name, args.db_username, args.db_userpassword))

if __name__ == "__main__":
    process_command_line(JoomlaImporter)