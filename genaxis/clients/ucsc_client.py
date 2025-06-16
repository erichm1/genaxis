import requests
import logging
from crispr.models import Gene, Species

logger = logging.getLogger(__name__)

BASE_URL = "https://api.genome.ucsc.edu"

def _build_url(endpoint, **params):
    """
    Monta a URL para UCSC API, usando ';' para separar parâmetros na query string.
    Exemplo: /getData/track?genome=hg38;track=refGene
    """
    if params:
        query = ";".join(f"{k}={v}" for k, v in params.items())
        url = f"{BASE_URL}/{endpoint}?{query}"
    else:
        url = f"{BASE_URL}/{endpoint}"
    logger.debug(f"Construída URL: {url}")
    return url

def list_ucsc_genomes():
    """
    Retorna a lista de genomas disponíveis no UCSC Genome Browser.
    """
    url = _build_url("list/ucscGenomes")
    logger.info(f"Solicitando genomas UCSC: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f"Resposta recebida com status {response.status_code}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Erro ao listar genomas UCSC: {e}")
        raise

def list_tracks(genome):
    """
    Retorna a lista de tracks disponíveis para um genoma UCSC.
    """
    url = _build_url("list/tracks", genome=genome)
    logger.info(f"Solicitando tracks para genoma '{genome}': {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f"Resposta recebida com status {response.status_code}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Erro ao listar tracks para genoma '{genome}': {e}")
        raise

def map_row_to_dict(data_row, columns):
    """
    Mapeia uma lista de valores (data_row) para um dicionário com keys nas colunas.
    """
    return dict(zip(columns, data_row))


def fetch_genes_for_species(genome="hg38", track="refGene", max_items=None):
    params = {
        "genome": genome,
        "track": track,
        "jsonOutputArrays": 1,
    }
    if max_items is not None:
        params["maxItemsOutput"] = str(max_items)

    url = _build_url("getData/track", **params)
    logger.info(f"Buscando genes para genoma '{genome}', track '{track}': {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Erro ao buscar genes: {e}")
        raise

    if track not in data:
        logger.warning(f"Track '{track}' não encontrado na resposta")
        return []

    column_types = data.get("columnTypes", [])
    columns = [col["name"] for col in column_types]
    track_data = data[track]

    species, _ = Species.objects.get_or_create(name="Caenorhabditis elegans")

    genes_imported = 0
    for chrom_key, genes_list in track_data.items():
        for data_row in genes_list:
            gene_data = map_row_to_dict(data_row, columns)
            try:
                Gene.objects.create(
                    bin=gene_data["bin"],
                    name=gene_data["name"],
                    chrom=gene_data["chrom"],
                    strand=gene_data["strand"],
                    txStart=gene_data["txStart"],
                    txEnd=gene_data["txEnd"],
                    cdsStart=gene_data["cdsStart"],
                    cdsEnd=gene_data["cdsEnd"],
                    exonCount=gene_data["exonCount"],
                    exonStarts=gene_data["exonStarts"],
                    exonEnds=gene_data["exonEnds"],
                    score=gene_data["score"],
                    name2=gene_data["name2"],
                    cdsStartStat=gene_data["cdsStartStat"],
                    cdsEndStat=gene_data["cdsEndStat"],
                    exonFrames=gene_data["exonFrames"],
                    species=species,
                )
                genes_imported += 1
            except Exception as ex:
                logger.error(f"Erro ao importar gene: {ex} | Dados: {gene_data}")

    logger.info(f"Importação finalizada: {genes_imported} genes importados para a espécie '{species.name}'")
    return genes_imported

def fetch_sequence_for_region(genome, chrom, start, end, rev_comp=False):
    """
    Busca a sequência para uma região genômica no UCSC Genome Browser.
    """
    params = {
        "genome": genome,
        "chrom": chrom,
        "start": start,
        "end": end,
    }
    if rev_comp:
        params["revComp"] = 1
    url = _build_url("getData/sequence", **params)
    logger.info(f"Solicitando sequência para região {chrom}:{start}-{end} no genoma '{genome}': {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f"Resposta recebida com status {response.status_code}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Erro ao buscar sequência para região {chrom}:{start}-{end}: {e}")
        raise

def search_ucsc(term, genome, categories=None):
    """
    Realiza busca por termo no UCSC Genome Browser, podendo filtrar por categorias.
    """
    params = {
        "search": term,
        "genome": genome,
    }
    if categories:
        params["categories"] = categories
    url = _build_url("search", **params)
    logger.info(f"Buscando termo '{term}' no genoma '{genome}' com categorias '{categories}': {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        logger.info(f"Resposta recebida com status {response.status_code}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Erro na busca UCSC para termo '{term}': {e}")
        raise
