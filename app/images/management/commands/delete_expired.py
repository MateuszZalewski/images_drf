from django.core.management.base import BaseCommand
from django.utils import timezone

from images.models import ExpiringLink


class Command(BaseCommand):
    help = "Delete expired links from database"

    def handle(self, *args, **options):
        now = timezone.now()
        expired_links = ExpiringLink.objects.filter(expiring__lte=now)
        if expired_links:
            count = expired_links.count()
            expired_links.delete()
            self.stdout.write(f"{count} expired links just got deleted.")
        else:
            self.stdout.write("No expired links to delete.")
