from django.core.management.base import BaseCommand
from crispr.models import Species, Gene
from clients.ucsc_client import fetch_genes_for_species


class Command(BaseCommand):
    help = "Importa genes da UCSC Genome API para uma espécie"

    def add_arguments(self, parser):
        parser.add_argument(
            'species_name', type=str, help='Nome da espécie (ex: Homo sapiens)'
        )
        parser.add_argument(
            'genome', type=str, help='Código do genoma UCSC (ex: hg38)'
        )

    def handle(self, *args, **options):
        species_name = options['species_name']
        genome = options['genome']

        species, created = Species.objects.get_or_create(name=species_name)
        if created:
            self.stdout.write(f"Espécie '{species_name}' criada.")

        # Obtemos a lista de genes (espera-se que essa função retorne uma lista de dicionários)
        genes = fetch_genes_for_species(genome=genome)
        total_genes = fetch_genes_for_species(genome=genome)
        self.stdout.write(f"Total de genes recebidos: {total_genes}")

        for i, gene_data in enumerate(genes, start=1):
            try:
                def safe_list_field(value):
                    if isinstance(value, list):
                        return ",".join(str(v) for v in value)
                    return value or ""

                strand_val = gene_data.get('strand')
                if isinstance(strand_val, int):
                    strand = '+' if strand_val == 1 else '-'
                elif isinstance(strand_val, str):
                    strand = strand_val
                else:
                    strand = '?'

                gene_defaults = {
                    'bin': gene_data.get('bin'),
                    'chrom': gene_data.get('chrom'),
                    'strand': strand,
                    'txStart': gene_data.get('txStart'),
                    'txEnd': gene_data.get('txEnd'),
                    'cdsStart': gene_data.get('cdsStart'),
                    'cdsEnd': gene_data.get('cdsEnd'),
                    'exonCount': gene_data.get('exonCount'),
                    'exonStarts': safe_list_field(gene_data.get('exonStarts')),
                    'exonEnds': safe_list_field(gene_data.get('exonEnds')),
                    'score': gene_data.get('score'),
                    'exonFrames': safe_list_field(gene_data.get('exonFrames')),
                }

                gene_name = gene_data.get('name2') or gene_data.get('name') or "unknown"

                Gene.objects.update_or_create(
                    species=species,
                    name=gene_name,
                    defaults=gene_defaults
                )

                if i % 100 == 0 or i == total_genes:
                    self.stdout.write(f"{i} genes importados...")

            except Exception as e:
                self.stderr.write(
                    f"Erro ao importar gene {gene_data.get('name', 'unknown')}: {e}"
                )

        self.stdout.write(
            f"Importação finalizada: {total_genes} genes importados para a espécie '{species_name}'"
        )
