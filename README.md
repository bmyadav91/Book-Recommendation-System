# Book-Recommendation-System

dataset file link: https://gist.github.com/jaidevd/23aef12e9bf56c618c41

## run setup.py
`pip install -e`

## .env setup
`copy all variables from .env-example.txt and create a .env file and paste it along with your credentials`

## s3 bucket setup
create your s3 bucket and setup in `.env` and `settings.py` for folder_name (give your project folder name)

### push static folder to s3 bucket from working directory using aws cli
`aws s3 cp .\static s3://pw-project-in/book_recommendation_system/static --recursive`

### update/change your s3 bucket policy 
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your_bucket_name_here/*",
    }
  ]
}
```