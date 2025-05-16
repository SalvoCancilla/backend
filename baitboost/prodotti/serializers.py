from rest_framework import serializers
from .models import Categoria, Brand, Product, ProductImage, Mulinello, Canna, Esca


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer per le categorie di prodotti"""
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'slug', 'descrizione', 'immagine', 'parent', 'ordine']


class BrandSerializer(serializers.ModelSerializer):
    """Serializer per i brand dei prodotti"""
    class Meta:
        model = Brand
        fields = ['id', 'nome', 'slug', 'descrizione', 'logo', 'sito_web']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer per le immagini dei prodotti"""
    class Meta:
        model = ProductImage
        fields = ['id', 'immagine', 'alt_text', 'is_principale', 'ordine']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer base per tutti i prodotti"""
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source='categoria',
        write_only=True
    )
    brand = BrandSerializer(read_only=True)
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.all(),
        source='brand',
        write_only=True
    )
    immagini = ProductImageSerializer(many=True, read_only=True)
    sconto_percentuale = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'nome', 'slug', 'codice_sku', 
            'categoria', 'categoria_id', 'brand', 'brand_id',
            'descrizione_breve', 'descrizione_completa', 'immagine_principale',
            'prezzo', 'prezzo_scontato', 'sconto_percentuale',
            'quantita_disponibile', 'is_in_stock', 'is_on_sale',
            'peso', 'in_evidenza', 'in_vendita', 'nuovo', 'usato', 'condizione',
            'immagini', 'meta_titolo', 'meta_descrizione', 'meta_keywords',
            'data_creazione', 'data_aggiornamento'
        ]


class MulinelloSerializer(ProductSerializer):
    """Serializer specifico per i mulinelli"""
    class Meta(ProductSerializer.Meta):
        model = Mulinello
        fields = ProductSerializer.Meta.fields + [
            'tipo_mulinello', 'materiale_corpo', 'cuscinetti', 'rapporto_recupero',
            'peso_mulinello', 'capacita_bobina', 'freno_massimo', 'frizione',
            'bobina_di_ricambio'
        ]


class CannaSerializer(ProductSerializer):
    """Serializer specifico per le canne da pesca"""
    class Meta(ProductSerializer.Meta):
        model = Canna
        fields = ProductSerializer.Meta.fields + [
            'tipo_canna', 'lunghezza', 'numero_sezioni', 'potenza_lancio',
            'azione', 'materiale', 'ingombro', 'anelli', 'porta_mulinello'
        ]


class EscaSerializer(ProductSerializer):
    """Serializer specifico per le esche"""
    class Meta(ProductSerializer.Meta):
        model = Esca
        fields = ProductSerializer.Meta.fields + [
            'tipo_esca', 'categoria_artificiale', 'lunghezza_esca', 'peso_esca',
            'profondita_lavoro', 'colore', 'galleggiante', 'ancorette',
            'rattlin', 'specie_target'
        ]
