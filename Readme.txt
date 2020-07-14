social_network_website is a Rest api service, where users can
signup/signin, create posts, like them, check other user activity, and likes analytics.
In addition there is an bot tool, which allows users
to create random users, with random posts, and add likes between them, also randomly.
It is implemented using config file uploading.

Liking and unliking posts are implemented via websockets, using Django channels.
Bot config file processing is implemented using background celery task, which,
sends response to user via channels after finishing its work.

Deployment is implemented using docker, with very simple setup.
Deployment steps:
    1. 

