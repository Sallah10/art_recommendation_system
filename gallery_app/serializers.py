from rest_framework import serializers
from .models import Art_Work, UserInteraction

class Art_Work_Serializer(serializers.ModelSerializer):
	class Meta:
		model = Art_Work
		fields = ('id', 'artiste', 'art_title', 'art_image',)

class UserInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteraction
        fields = '__all__'