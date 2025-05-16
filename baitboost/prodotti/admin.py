from django.contrib import admin
from .models import (
    Categoria, Brand, Product, ProductImage,
    Mulinello, Canna, Esca
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['immagine', 'alt_text', 'is_principale', 'ordine']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'parent', 'ordine']
    list_filter = ['parent']
    search_fields = ['nome', 'descrizione']
    prepopulated_fields = {'slug': ('nome',)}
    list_editable = ['ordine']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sito_web']
    search_fields = ['nome', 'descrizione']
    prepopulated_fields = {'slug': ('nome',)}


class ProductAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codice_sku', 'categoria', 'brand', 'prezzo', 
                    'prezzo_scontato', 'quantita_disponibile', 'in_evidenza', 'in_vendita']
    list_filter = ['categoria', 'brand', 'in_evidenza', 'in_vendita', 'nuovo', 'usato']
    search_fields = ['nome', 'descrizione_breve', 'codice_sku']
    prepopulated_fields = {'slug': ('nome',)}
    readonly_fields = ['data_creazione', 'data_aggiornamento']
    fieldsets = [
        ('Informazioni Principali', {
            'fields': ('nome', 'slug', 'codice_sku', 'categoria', 'brand')
        }),
        ('Descrizioni', {
            'fields': ('descrizione_breve', 'descrizione_completa')
        }),
        ('Immagine Principale', {
            'fields': ('immagine_principale',)
        }),
        ('Prezzo e Stock', {
            'fields': ('prezzo', 'prezzo_scontato', 'quantita_disponibile', 'peso')
        }),
        ('Opzioni Prodotto', {
            'fields': ('in_evidenza', 'in_vendita', 'nuovo', 'usato', 'condizione')
        }),
        ('SEO', {
            'fields': ('meta_titolo', 'meta_descrizione', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('data_creazione', 'data_aggiornamento'),
            'classes': ('collapse',)
        }),
    ]
    inlines = [ProductImageInline]


@admin.register(Mulinello)
class MulinelloAdmin(ProductAdmin):
    fieldsets = ProductAdmin.fieldsets + [
        ('Specifiche Mulinello', {
            'fields': ('tipo_mulinello', 'materiale_corpo', 'cuscinetti', 'rapporto_recupero', 
                      'peso_mulinello', 'capacita_bobina', 'freno_massimo', 'frizione', 'bobina_di_ricambio')
        }),
    ]


@admin.register(Canna)
class CannaAdmin(ProductAdmin):
    fieldsets = ProductAdmin.fieldsets + [
        ('Specifiche Canna', {
            'fields': ('tipo_canna', 'lunghezza', 'numero_sezioni', 'potenza_lancio', 
                      'azione', 'materiale', 'ingombro', 'anelli', 'porta_mulinello')
        }),
    ]


@admin.register(Esca)
class EscaAdmin(ProductAdmin):
    fieldsets = ProductAdmin.fieldsets + [
        ('Specifiche Esca', {
            'fields': ('tipo_esca', 'categoria_artificiale', 'lunghezza_esca', 'peso_esca', 
                      'profondita_lavoro', 'colore', 'galleggiante', 'ancorette', 'rattlin', 'specie_target')
        }),
    ]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['prodotto', 'immagine', 'is_principale', 'ordine']
    list_filter = ['is_principale']
    search_fields = ['prodotto__nome', 'alt_text']
    list_editable = ['is_principale', 'ordine']
