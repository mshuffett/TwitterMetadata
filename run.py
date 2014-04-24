from tweetid import db
from tweetid.tsv import process_tsv

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    process_tsv(
        'C:/Users/Michael/Downloads/twitterdata_oklahomatornado-20130520_20130530_GMT.tsv/twitterdata_oklahomatornado-vFULL-3.tsv',
        count=100)
    # app.run(debug=True)
