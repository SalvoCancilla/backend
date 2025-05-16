from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg

from .models import (
    Categoria, Brand, Product, 
    ProductImage, Mulinello, Canna, Esca
)
from .serializers import (
    CategoriaSerializer, BrandSerializer, ProductSerializer,
    ProductImageSerializer, MulinelloSerializer, CannaSerializer, EscaSerializer
)
from .filters import ProductFilter, MulinelloFilter, CannaFilter, EscaFilter


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    API endpoint per le categorie di prodotti
    Permette visualizzazione, creazione, modifica e cancellazione di categorie
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descrizione']
    ordering_fields = ['nome', 'ordine']
    ordering = ['ordine']
    
    def get_permissions(self):
        """Solo lettura per utenti non autenticati"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def prodotti(self, request, slug=None):
        """Restituisce i prodotti appartenenti a una categoria"""
        categoria = self.get_object()
        prodotti = Product.objects.filter(categoria=categoria)
        serializer = ProductSerializer(prodotti, many=True)
        return Response(serializer.data)


class BrandViewSet(viewsets.ModelViewSet):
    """
    API endpoint per i brand/produttori
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descrizione']
    ordering_fields = ['nome']
    ordering = ['nome']
    
    def get_permissions(self):
        """Solo lettura per utenti non autenticati"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def prodotti(self, request, slug=None):
        """Restituisce i prodotti di un determinato brand"""
        brand = self.get_object()
        prodotti = Product.objects.filter(brand=brand)
        serializer = ProductSerializer(prodotti, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint per tutti i prodotti
    Implementa filtri avanzati sia per ricerca testuale che per campi specifici
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['nome', 'descrizione_breve', 'descrizione_completa', 'codice_sku']
    ordering_fields = [
        'nome', 'prezzo', 'prezzo_scontato', 'data_creazione', 
        'quantita_disponibile', 'brand__nome', 'categoria__nome'
    ]
    ordering = ['-data_creazione']
    
    def get_permissions(self):
        """Solo lettura per utenti non autenticati"""
        if self.action in ['list', 'retrieve', 'in_evidenza', 'nuovi_arrivi', 'in_sconto']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def in_evidenza(self, request):
        """Restituisce i prodotti in evidenza"""
        prodotti = self.get_queryset().filter(in_evidenza=True)
        serializer = self.get_serializer(prodotti, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def nuovi_arrivi(self, request):
        """Restituisce i prodotti più recenti (ultimi 30 giorni)"""
        from django.utils import timezone
        from datetime import timedelta
        
        data_limite = timezone.now() - timedelta(days=30)
        prodotti = self.get_queryset().filter(data_creazione__gte=data_limite)
        serializer = self.get_serializer(prodotti, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def in_sconto(self, request):
        """Restituisce i prodotti in sconto"""
        from django.db.models import F
        
        prodotti = self.get_queryset().filter(
            prezzo_scontato__isnull=False
        ).filter(prezzo_scontato__lt=F('prezzo'))
        
        serializer = self.get_serializer(prodotti, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistiche(self, request):
        """
        Restituisce statistiche sui prodotti per il pannello di controllo
        Richiede autorizzazione da admin
        """
        permission_classes = [IsAdminUser]
        
        total_products = Product.objects.count()
        products_in_stock = Product.objects.filter(quantita_disponibile__gt=0).count()
        products_out_of_stock = Product.objects.filter(quantita_disponibile=0).count()
        products_on_sale = Product.objects.filter(prezzo_scontato__isnull=False).count()
        
        products_by_category = Categoria.objects.annotate(
            product_count=Count('prodotti')
        ).values('nome', 'product_count')
        
        products_by_brand = Brand.objects.annotate(
            product_count=Count('prodotti')
        ).values('nome', 'product_count')
        
        return Response({
            'total_products': total_products,
            'products_in_stock': products_in_stock,
            'products_out_of_stock': products_out_of_stock,
            'products_on_sale': products_on_sale,
            'products_by_category': products_by_category,
            'products_by_brand': products_by_brand,
        })
    
    
class MulinelloViewSet(viewsets.ModelViewSet):
    """
    API endpoint per i mulinelli
    Implementa filtri avanzati specifici per i mulinelli
    """
    queryset = Mulinello.objects.all()
    serializer_class = MulinelloSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MulinelloFilter
    search_fields = ['nome', 'descrizione_breve', 'descrizione_completa', 'codice_sku']
    ordering_fields = [
        'nome', 'prezzo', 'prezzo_scontato', 'data_creazione', 
        'cuscinetti', 'peso_mulinello', 'freno_massimo'
    ]
    ordering = ['-data_creazione']
    
    def get_permissions(self):
        """Solo lettura per utenti non autenticati"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class CannaViewSet(viewsets.ModelViewSet):
    """
    API endpoint per le canne da pesca
    Implementa filtri avanzati specifici per le canne
    """
    queryset = Canna.objects.all()
    serializer_class = CannaSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CannaFilter
    search_fields = ['nome', 'descrizione_breve', 'descrizione_completa', 'codice_sku']
    ordering_fields = [
        'nome', 'prezzo', 'prezzo_scontato', 'data_creazione', 
        'lunghezza', 'ingombro'
    ]
    ordering = ['-data_creazione']
    
    def get_permissions(self):
        """Solo lettura per utenti non autenticati"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class EscaViewSet(viewsets.ModelViewSet):
    """
    API endpoint per le esche
    Implementa filtri avanzati specifici per le esche
    """
    queryset = Esca.objects.all()
    serializer_class = EscaSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EscaFilter
    search_fields = ['nome', 'descrizione_breve', 'descrizione_completa', 'codice_sku', 'specie_target']
    ordering_fields = [
        'nome', 'prezzo', 'prezzo_scontato', 'data_creazione', 
        'lunghezza_esca', 'peso_esca'
    ]
    ordering = ['-data_creazione']
    
    def get_permissions(self):
        """Solo lettura per utenti non autenticati"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
