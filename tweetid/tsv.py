import csv
import tarfile

from models import Tweet, Collection


def process_tar(path, count=0):
    """
    Load the tar at path into database. If count is positive, limit number of tweets to load to count tweets.
    """
    tweets = []
    with tarfile.open(path, mode='r:gz') as tar:
        member = tar.getmembers()[0]  # assume single file tar
        f = tar.extractfile(member)
        tsv = csv.reader(f, delimiter='\t')
        for i, row in enumerate(tsv):
            if row[-1] != '\\N' or row[-2] != '\\N':
                print row
                raise Exception('Unexpected format.')
            row = row[:-2]

            tweets.append(Tweet(*row))

    oollection = Collection(tweets=tweets)
    collection.save()
    # print oollection.start_date, oollection.end_date

process_tar('C:/Users/Michael/Downloads/twitterdata_oklahomatornado-20130520_20130530_GMT.tsv.tar.gz')