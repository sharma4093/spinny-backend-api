from rest_framework import serializers
from .models import Box

class BoxSerializer(serializers.ModelSerializer):
    area = serializers.SerializerMethodField()
    volume = serializers.SerializerMethodField()
    class Meta:
        model = Box
        fields = ['length', 'width', 'height','area', 'volume']
    
    def get_area(self, obj):
        return 2*((obj.length*obj.width)+(obj.length*obj.height)+(obj.height*obj.width))

    def get_volume(self, obj):
        return obj.length * obj.width * obj.height

class BoxFullSerializer(serializers.ModelSerializer):
    area = serializers.SerializerMethodField()
    volume = serializers.SerializerMethodField()
    class Meta:
        model = Box
        fields = ['length', 'width', 'height','area', 'volume' ,'created_at', 'updated_at']
    
    def get_area(self, obj):
        return 2*((obj.length*obj.width)+(obj.length*obj.height)+(obj.height*obj.width))

    def get_volume(self, obj):
        return obj.length * obj.width * obj.height