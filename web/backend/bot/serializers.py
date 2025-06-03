from rest_framework import serializers
from .models import Configuration, ActionLog

class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = ['system_prompt', 'style', 'temperature', 'top_k', 'max_token']
        
    def validate_temperature(self, value):
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Temperature must be between 0 and 1.")
        return value
    
    def validate_top_k(self, value):
        if not 1 <= value <= 100:
            raise serializers.ValidationError("Top K must be between 1 and 100.")
        return value
    
    def validate_max_token(self, value):
        if not 1 <= value <= 4096:
            raise serializers.ValidationError("Max tokens must be between 1 and 4096.")
        return value

class ActionLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ActionLog
        fields = ['id', 'username', 'action_type', 'target', 'status', 'message', 'timestamp']
        read_only_fields = ['id', 'username', 'timestamp']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Format timestamp for frontend
        data['timestamp'] = instance.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return data