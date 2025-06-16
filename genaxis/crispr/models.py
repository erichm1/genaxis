from django.db import models
import uuid

class Species(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)  # ex: Homo sapiens
    scientific_name = models.CharField(max_length=150, blank=True)
    common_name = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Species"


class Gene(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    species = models.ForeignKey('Species', related_name='genes', on_delete=models.CASCADE)

    sequence = models.TextField(help_text="Full gene sequence", blank=True, null=True)  # Adicionado para CrisprEdit

    bin = models.PositiveSmallIntegerField(help_text="Indexing field for fast queries", blank=True, null=True)
    chrom = models.CharField(max_length=255, help_text="Chromosome or scaffold", blank=True, null=True)
    strand = models.CharField(
        max_length=1, 
        choices=[('+', '+'), ('-', '-')], 
        help_text="Strand direction", 
        blank=True, 
        null=True
    )
    txStart = models.PositiveIntegerField(help_text="Transcription start", blank=True, null=True)
    txEnd = models.PositiveIntegerField(help_text="Transcription end", blank=True, null=True)
    cdsStart = models.PositiveIntegerField(help_text="CDS start", blank=True, null=True)
    cdsEnd = models.PositiveIntegerField(help_text="CDS end", blank=True, null=True)
    exonCount = models.PositiveIntegerField(help_text="Number of exons", blank=True, null=True)
    exonStarts = models.TextField(help_text="Comma-separated exon starts", blank=True, null=True)
    exonEnds = models.TextField(help_text="Comma-separated exon ends", blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    exonFrames = models.TextField(help_text="Exon reading frames", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.species.name} - {self.chrom or 'Unknown chrom'}"

    class Meta:
        verbose_name_plural = "Genes"


class CrisprEdit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE, related_name='edits')
    target_sequence = models.CharField(max_length=100)
    replacement_sequence = models.CharField(max_length=100)
    edited_sequence = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Edit on {self.gene}"

    def save(self, *args, **kwargs):
        original_sequence = self.gene.sequence or ""
        if self.target_sequence in original_sequence:
            self.edited_sequence = original_sequence.replace(
                self.target_sequence, self.replacement_sequence
            )
        else:
            self.edited_sequence = original_sequence
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "CRISPR Edits"
