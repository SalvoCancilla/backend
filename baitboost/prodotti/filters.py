from django import forms
from django.db.models import Q, F
from django.utils import timezone
from django_filters import rest_framework as filters

from .models import Product, Mulinello, Canna, Esca, Categoria, Brand


class ProductFilter(filters.FilterSet):
    """
    Filtro generico per tutti i prodotti
    Permette ricerche testuali e filtri sui campi comuni
    """
    # Ricerca testuale globale
    query = filters.CharFilter(method='filter_query', label='Ricerca globale')
    
    # Filtri sui campi comuni
    nome = filters.CharFilter(lookup_expr='icontains', label='Nome')
    categoria = filters.ModelChoiceFilter(queryset=Categoria.objects.all(), label='Categoria')
    categorie = filters.ModelMultipleChoiceFilter(
        queryset=Categoria.objects.all(),
        field_name='categoria',
        label='Categorie (multiple)'
    )
    brand = filters.ModelChoiceFilter(queryset=Brand.objects.all(), label='Brand')
    brands = filters.ModelMultipleChoiceFilter(
        queryset=Brand.objects.all(),
        field_name='brand',
        label='Brands (multiple)'
    )
    
    # Filtri sui prezzi
    prezzo_min = filters.NumberFilter(field_name='prezzo', lookup_expr='gte', label='Prezzo minimo')
    prezzo_max = filters.NumberFilter(field_name='prezzo', lookup_expr='lte', label='Prezzo massimo')
    in_sconto = filters.BooleanFilter(method='filter_in_sconto', label='In sconto')
    
    # Filtri sulla disponibilità
    disponibile = filters.BooleanFilter(method='filter_disponibile', label='Disponibile')
    nuovo = filters.BooleanFilter(field_name='nuovo', label='Nuovo')
    usato = filters.BooleanFilter(field_name='usato', label='Usato')
    
    # Filtri aggiuntivi
    in_evidenza = filters.BooleanFilter(field_name='in_evidenza', label='In evidenza')
    recente = filters.BooleanFilter(method='filter_recente', label='Prodotti recenti')
    
    class Meta:
        model = Product
        fields = [
            'nome', 'categoria', 'brand', 'prezzo_min', 'prezzo_max', 
            'in_sconto', 'disponibile', 'nuovo', 'usato', 'in_evidenza'
        ]
    
    def filter_query(self, queryset, name, value):
        """Ricerca testuale su più campi contemporaneamente"""
        if not value:
            return queryset
        
        # Ricerca nei campi principali per tutti i prodotti
        return queryset.filter(
            Q(nome__icontains=value) |
            Q(descrizione_breve__icontains=value) |
            Q(descrizione_completa__icontains=value) |
            Q(codice_sku__icontains=value) |
            Q(brand__nome__icontains=value) |
            Q(categoria__nome__icontains=value)
        ).distinct()
    
    def filter_in_sconto(self, queryset, name, value):
        """Filtra prodotti in sconto"""
        if value:
            return queryset.filter(prezzo_scontato__isnull=False).filter(prezzo_scontato__lt=models.F('prezzo'))
        return queryset
    
    def filter_disponibile(self, queryset, name, value):
        """Filtra prodotti disponibili"""
        if value:
            return queryset.filter(quantita_disponibile__gt=0)
        return queryset
    
    def filter_recente(self, queryset, name, value):
        """Filtra prodotti aggiunti recentemente (ultimi 30 giorni)"""
        if value:
            thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
            return queryset.filter(data_creazione__gte=thirty_days_ago)
        return queryset


class MulinelloFilter(ProductFilter):
    """
    Filtri specifici per mulinelli, estende i filtri base dei prodotti
    """
    # Filtri specifici per i mulinelli
    tipo_mulinello = filters.ChoiceFilter(
        choices=Mulinello._meta.get_field('tipo_mulinello').choices,
        label='Tipo di mulinello'
    )
    cuscinetti_min = filters.NumberFilter(field_name='cuscinetti', lookup_expr='gte', label='Cuscinetti minimo')
    cuscinetti_max = filters.NumberFilter(field_name='cuscinetti', lookup_expr='lte', label='Cuscinetti massimo')
    frizione = filters.ChoiceFilter(
        choices=Mulinello._meta.get_field('frizione').choices,
        label='Tipo di frizione'
    )
    bobina_di_ricambio = filters.BooleanFilter(field_name='bobina_di_ricambio', label='Con bobina di ricambio')
    peso_max = filters.NumberFilter(field_name='peso_mulinello', lookup_expr='lte', label='Peso massimo (g)')
    freno_min = filters.NumberFilter(field_name='freno_massimo', lookup_expr='gte', label='Potenza freno minima (kg)')
    
    class Meta(ProductFilter.Meta):
        model = Mulinello
        fields = ProductFilter.Meta.fields + [
            'tipo_mulinello', 'cuscinetti_min', 'cuscinetti_max', 
            'frizione', 'bobina_di_ricambio', 'peso_max', 'freno_min'
        ]


class CannaFilter(ProductFilter):
    """
    Filtri specifici per canne da pesca, estende i filtri base dei prodotti
    """
    # Filtri specifici per le canne
    tipo_canna = filters.ChoiceFilter(
        choices=Canna._meta.get_field('tipo_canna').choices,
        label='Tipo di canna'
    )
    lunghezza_min = filters.NumberFilter(field_name='lunghezza', lookup_expr='gte', label='Lunghezza minima (m)')
    lunghezza_max = filters.NumberFilter(field_name='lunghezza', lookup_expr='lte', label='Lunghezza massima (m)')
    azione = filters.ChoiceFilter(
        choices=Canna._meta.get_field('azione').choices,
        label='Azione della canna'
    )
    materiale = filters.CharFilter(field_name='materiale', lookup_expr='icontains', label='Materiale')
    ingombro_max = filters.NumberFilter(field_name='ingombro', lookup_expr='lte', label='Ingombro massimo (cm)')
    
    # Filtri per potenza di lancio
    # Nota: questo è un po' complesso perché potenza_lancio è una stringa come "10-30g"
    potenza_min = filters.CharFilter(method='filter_potenza_min', label='Potenza lancio minima')
    potenza_max = filters.CharFilter(method='filter_potenza_max', label='Potenza lancio massima')
    
    class Meta(ProductFilter.Meta):
        model = Canna
        fields = ProductFilter.Meta.fields + [
            'tipo_canna', 'lunghezza_min', 'lunghezza_max', 
            'azione', 'materiale', 'ingombro_max',
            'potenza_min', 'potenza_max'
        ]
    
    def filter_potenza_min(self, queryset, name, value):
        """
        Filtra canne con potenza minima >= al valore specificato
        Esempio: se potenza_lancio = "10-30g" e value = "15g", la canna viene filtrata
        """
        if not value:
            return queryset
        
        # Rimuoviamo l'unità di misura se presente
        value = value.replace('g', '').replace('G', '').strip()
        
        try:
            value_num = float(value)
            filtered_canne = []
            
            for canna in queryset:
                if not canna.potenza_lancio:
                    continue
                
                # Estrai il valore minimo dalla stringa "min-max"
                potenza = canna.potenza_lancio.lower().replace('g', '')
                if '-' in potenza:
                    min_val = float(potenza.split('-')[0])
                    if min_val >= value_num:
                        filtered_canne.append(canna.id)
            
            return queryset.filter(id__in=filtered_canne)
        except (ValueError, AttributeError):
            # In caso di errore nella conversione, ritorna il queryset originale
            return queryset
    
    def filter_potenza_max(self, queryset, name, value):
        """
        Filtra canne con potenza massima <= al valore specificato
        Esempio: se potenza_lancio = "10-30g" e value = "25g", la canna viene filtrata
        """
        if not value:
            return queryset
        
        # Rimuoviamo l'unità di misura se presente
        value = value.replace('g', '').replace('G', '').strip()
        
        try:
            value_num = float(value)
            filtered_canne = []
            
            for canna in queryset:
                if not canna.potenza_lancio:
                    continue
                
                # Estrai il valore massimo dalla stringa "min-max"
                potenza = canna.potenza_lancio.lower().replace('g', '')
                if '-' in potenza:
                    max_val = float(potenza.split('-')[1])
                    if max_val <= value_num:
                        filtered_canne.append(canna.id)
            
            return queryset.filter(id__in=filtered_canne)
        except (ValueError, AttributeError):
            # In caso di errore nella conversione, ritorna il queryset originale
            return queryset


class EscaFilter(ProductFilter):
    """
    Filtri specifici per esche, estende i filtri base dei prodotti
    """
    # Filtri specifici per le esche
    tipo_esca = filters.ChoiceFilter(
        choices=Esca._meta.get_field('tipo_esca').choices,
        label='Tipo di esca'
    )
    categoria_artificiale = filters.ChoiceFilter(
        choices=Esca._meta.get_field('categoria_artificiale').choices,
        label='Categoria artificiale'
    )
    lunghezza_min = filters.NumberFilter(field_name='lunghezza_esca', lookup_expr='gte', label='Lunghezza minima (cm)')
    lunghezza_max = filters.NumberFilter(field_name='lunghezza_esca', lookup_expr='lte', label='Lunghezza massima (cm)')
    peso_min = filters.NumberFilter(field_name='peso_esca', lookup_expr='gte', label='Peso minimo (g)')
    peso_max = filters.NumberFilter(field_name='peso_esca', lookup_expr='lte', label='Peso massimo (g)')
    profondita = filters.CharFilter(field_name='profondita_lavoro', lookup_expr='icontains', label='Profondità di lavoro')
    colore = filters.CharFilter(field_name='colore', lookup_expr='icontains', label='Colore')
    galleggiante = filters.BooleanFilter(field_name='galleggiante', label='Galleggiante')
    rattlin = filters.BooleanFilter(field_name='rattlin', label='Con suoni/vibrazioni')
    specie_target = filters.CharFilter(field_name='specie_target', lookup_expr='icontains', label='Specie target')
    
    class Meta(ProductFilter.Meta):
        model = Esca
        fields = ProductFilter.Meta.fields + [
            'tipo_esca', 'categoria_artificiale', 'lunghezza_min', 
            'lunghezza_max', 'peso_min', 'peso_max', 'profondita',
            'colore', 'galleggiante', 'rattlin', 'specie_target'
        ]
