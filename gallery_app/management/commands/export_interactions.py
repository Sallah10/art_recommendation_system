import csv
from django.core.management.base import BaseCommand
from gallery_app.models import UserInteraction

class Command(BaseCommand):
  """Export user interactions to CSV"""

  def handle(self, *args, **kwargs):
    interactions = UserInteraction.objects.all()
    with open('interactions.csv', 'w', newline='') as csvfile:
      fieldnames = ['user', 'artwork', 'liked', 'bookmarked', 'view_count', 'last_interacted']
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

      writer.writeheader()
      for interaction in interactions:
        writer.writerow({
          'user': interaction.user.id,
          'artwork': interaction.artwork.id,
          'liked': interaction.liked,
          'bookmarked': interaction.bookmarked,
          'view_count': interaction.view_count,
          'last_interacted': interaction.last_interacted,
        })

    self.stdout.write(self.style.SUCCESS('Successfully exported interactions'))
