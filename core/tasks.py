from celery.utils.log import get_task_logger
from celery import shared_task

logger = get_task_logger(__name__)


@shared_task(name="test_demo")
def demo():
    print("hello from task")
    