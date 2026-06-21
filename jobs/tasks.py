from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_status_update_email(self, candidate_email, candidate_username, job_title, new_status):
    """
    Send an email notification to a candidate when their application
    status changes. Retries up to 3 times on failure, with 60 second delay.
    """
    status_messages = {
        'reviewed': 'Your application is being reviewed.',
        'accepted': 'Congratulations! Your application has been accepted.',
        'rejected': 'Unfortunately, your application was not successful.',
    }

    message = status_messages.get(new_status, f'Your application status has been updated to {new_status}.')

    try:
        send_mail(
            subject=f'Application Update: {job_title}',
            message=f'Hi {candidate_username},\n\n{message}\n\nJob: {job_title}\nStatus: {new_status.capitalize()}\n\nBest regards,\nJob Board Team',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[candidate_email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)