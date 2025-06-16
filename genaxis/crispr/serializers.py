from rest_framework import serializers
from .models import Species, Gene, CrisprEdit

class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = '__all__'

class GeneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gene
        fields = '__all__'

class CrisprEditSerializer(serializers.ModelSerializer):
    gene = GeneSerializer(read_only=True)
    gene_id = serializers.PrimaryKeyRelatedField(queryset=Gene.objects.all(), write_only=True)

    class Meta:
        model = CrisprEdit
        fields = ['id', 'gene', 'gene_id', 'target_sequence', 'replacement_sequence', 'edited_sequence', 'created_at']
        read_only_fields = ['edited_sequence', 'created_at']