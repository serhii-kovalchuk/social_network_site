import logging
import random

from asgiref.sync import sync_to_async, async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from social_network_site.celery import app

from core.models import User, Like, Post
from core.utils import account_activation_token, get_random_string


@app.task
def send_verification_mail_task(user_id, force=False):
    UserModel = get_user_model()
    try:
        user = UserModel.objects.get(pk=user_id)

        mail_subject = 'Activate your account'
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        current_site = "{}/email/activation".format(settings.HOST)
        activation_link = "{0}/{1}/{2}/".format(current_site, str(uid), token)

        message = f"Please, click the link to confirm your email {activation_link}"
        email = EmailMessage(mail_subject, message, to=[user.email])

        # Just to show an idea
        # email.send()

    except UserModel.DoesNotExist:
        logging.warning(
            f"Tried to send verification email to non-existing user with {user_id}")


def get_random_user_data():
    username = get_random_string(10)
    email = username + '@gmail.com'
    password = email
    return {"username": username, "email": email, "password": password}


def get_random_post_data():
    topic = get_random_string(10)
    text = get_random_string(10)
    return {"topic": topic, "text": text}


def get_random_like_data(posts_ids):
    post_id = random.choice(posts_ids)
    return {"post_id": post_id}


@app.task
def bot_process(user_id, data):
    print(data)

    number_of_users = data["number_of_users"]
    max_posts_per_user = data["max_posts_per_user"]
    max_likes_per_user = data["max_likes_per_user"]

    # algorithm is not ideal,
    # because users can like their own posts,
    # but for the sake of better readability was decided to make it so

    new_users_ids_start = User.objects.last().id + 1
    new_users_ids_end = new_users_ids_start + number_of_users - 1
    new_users_ids_range = range(new_users_ids_start, new_users_ids_end + 1)

    User.objects.bulk_create(
        User.objects.initialize_user(**get_random_user_data())
        for _ in range(number_of_users)
    )

    new_posts_ids_start = Post.objects.last().id + 1

    posts = Post.objects.bulk_create(
        Post(user_id=user_id, **get_random_post_data())
        for _ in range(random.randint(0, max_likes_per_user))
        for user_id in new_users_ids_range
    )
    new_posts_ids_end = new_posts_ids_start + len(posts) - 1
    new_posts_ids_range = range(new_posts_ids_start, new_posts_ids_end + 1)

    Like.objects.bulk_create(
        Like(user_id=user_id, **get_random_like_data(new_posts_ids_range))
        for _ in range(random.randint(0, max_posts_per_user))
        for user_id in new_users_ids_range
    )

    channel_layer = get_channel_layer()

    # Sends message to channels group in order to inform user
    async_to_sync(channel_layer.group_send)(
        f'ws_bot_{user_id}',
        {'type': 'message_from_bot', "message": "work is done"}
    )

    return None




