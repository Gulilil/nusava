# Instagram Stats Management Commands

`python manage.py update_instagram_stats username password`
## Schedule updates every 6 hours (default)
`python manage.py update_instagram_stats username password --schedule`

## Schedule updates every 2 hours
`python manage.py update_instagram_stats username password --schedule --hours 2`

## Schedule updates every hour
`python manage.py update_instagram_stats username password --schedule --hours 1`