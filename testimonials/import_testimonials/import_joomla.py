"""
Import the testimonials from joomla.
"""
from mezzanine.core.models import CONTENT_STATUS_PUBLISHED

from testimonials.models import Testimonial


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

    def import_testimonials(self, testimonial_rows):
        self.vprint("BEGIN Importing testimonials", 1)
        for row in testimonial_rows:
            self.vprint("    Importing row: {}/{}".format(row['author'], row['title']), 2)
            testimonial = self.get_or_create(Testimonial, **row)
            if not self.dry_run:
                # Assign created/updated date (this must be done after the first save)
                testimonial.status = CONTENT_STATUS_PUBLISHED
                testimonial.save()

        self.vprint("END   Importing testimonials", 1)


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


def get_testimonial_rows(db_name, db_username, db_userpassword):
    """
    Return a full list of the testimonials as dict rows for further processing.
    This assumes there are not too many (<5,000).
    """
    qry = """
SELECT
    t_caption AS 'title',
    t_author AS 'author',
    testimonial AS 'content'
FROM
    jos_tm_testimonials
WHERE
    published = 1"""
    cursor = get_cursor(db_name, db_username, db_userpassword)
    cursor.execute(qry)
    return dictfetchall(cursor)


def process_command_line(importer_class):
    """
    Process the command line, passing the csv files and parameters to the importer_class
    """
    import argparse

    parser = argparse.ArgumentParser(description="Import Joomla testimonials as blog posts.")
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
    importer.import_testimonials(get_testimonial_rows(args.db_name, args.db_username, args.db_userpassword))

if __name__ == "__main__":
    process_command_line(JoomlaImporter)