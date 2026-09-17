from django.shortcuts import render
from django.http import HttpResponse
from .models import Art_Work, UserInteraction

from rest_framework.viewsets import ModelViewSet
from .serializers import Art_Work_Serializer, UserInteractionSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
def index(request):
	return HttpResponse('Hello')

class ArtWorks(ModelViewSet):
	queryset = Art_Work.objects.all()
	serializer_class = Art_Work_Serializer

class UserInteraction(ModelViewSet):
	queryset = UserInteraction.objects.all()
	serializer_class = UserInteractionSerializer

@api_view(['GET'])
def get_arts(request):
	arts = Art_Work.objects.all()
	serializer = Art_Work_Serializer(arts, many=True)
	return Response(serializer.data)


@api_view(['GET'])
def recommend_artworks(request, user_id):
    user_interactions = UserInteraction.objects.filter(user_id=user_id)
    interacted_artworks = [interaction.artwork_id for interaction in user_interactions]

    all_artworks = Artwork.objects.exclude(id__in=interacted_artworks)
    model = CollaborativeFiltering.load_model('path_to_model/collaborative_filtering_model.pth')

    user_tensor = torch.tensor([user_id] * len(all_artworks))
    artwork_tensors = torch.tensor([artwork.id for artwork in all_artworks])

    with torch.no_grad():
        scores = model(user_tensor, artwork_tensors).numpy()

    artwork_scores = zip(all_artworks, scores)
    recommended_artworks = sorted(artwork_scores, key=lambda x: x[1], reverse=True)[:10]  # Top 10 recommendations

    serialized_artworks = ArtworkSerializer([artwork for artwork, score in recommended_artworks], many=True)
    return Response(serialized_artworks.data)