from django.db import models
from django.utils.text import slugify
from django.urls import reverse
import uuid


class Categoria(models.Model):
    """Categoria di prodotti per la pesca sportiva"""
    nome = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    descrizione = models.TextField(blank=True, null=True)
    immagine = models.ImageField(upload_to='categorie/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sottocategorie')
    ordine = models.PositiveIntegerField(default=0)
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_aggiornamento = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorie'
        ordering = ['ordine', 'nome']
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('categoria-detail', kwargs={'slug': self.slug})


class Brand(models.Model):
    """Marchio o produttore di articoli da pesca"""
    nome = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    descrizione = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    sito_web = models.URLField(blank=True, null=True)
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_aggiornamento = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Modello base per tutti i prodotti di pesca sportiva"""
    # Campi identificativi
    nome = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    codice_sku = models.CharField(max_length=50, unique=True, blank=True)
    
    # Categorizzazione
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='prodotti')
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='prodotti')
    
    # Informazioni principali
    descrizione_breve = models.TextField()
    descrizione_completa = models.TextField(blank=True, null=True)
    immagine_principale = models.ImageField(upload_to='prodotti/')
    
    # Informazioni di prezzo e stock
    prezzo = models.DecimalField(max_digits=10, decimal_places=2)
    prezzo_scontato = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantita_disponibile = models.PositiveIntegerField(default=0)
    peso = models.DecimalField(max_digits=6, decimal_places=2, help_text='Peso in grammi', blank=True, null=True)
    
    # Flags e metadati
    in_evidenza = models.BooleanField(default=False)
    in_vendita = models.BooleanField(default=True)
    nuovo = models.BooleanField(default=False)
    usato = models.BooleanField(default=False)
    condizione = models.CharField(max_length=50, blank=True, null=True, 
                               help_text='Per prodotti usati, specificare lo stato (Ottimo, Buono, Usato, ecc.)')
    
    # Campi SEO
    meta_titolo = models.CharField(max_length=100, blank=True, null=True)
    meta_descrizione = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamp
    data_creazione = models.DateTimeField(auto_now_add=True)
    data_aggiornamento = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Prodotto'
        verbose_name_plural = 'Prodotti'
        ordering = ['-data_creazione']
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        # Genera slug se non esiste
        if not self.slug:
            self.slug = slugify(self.nome)
        
        # Genera SKU se non esiste
        if not self.codice_sku:
            # Crea un codice univoco basato su brand, categoria e uuid
            prefix = f"{self.brand.nome[:3].upper()}{self.categoria.nome[:3].upper()}"
            unique_id = str(uuid.uuid4())[:8]
            self.codice_sku = f"{prefix}-{unique_id}"
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})
    
    @property
    def is_in_stock(self):
        return self.quantita_disponibile > 0
    
    @property
    def is_on_sale(self):
        return self.prezzo_scontato is not None and self.prezzo_scontato < self.prezzo
    
    @property
    def sconto_percentuale(self):
        if self.is_on_sale:
            sconto = ((self.prezzo - self.prezzo_scontato) / self.prezzo) * 100
            return round(sconto)
        return 0


class ProductImage(models.Model):
    """Immagini aggiuntive per i prodotti"""
    prodotto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='immagini')
    immagine = models.ImageField(upload_to='prodotti/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_principale = models.BooleanField(default=False)
    ordine = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Immagine prodotto'
        verbose_name_plural = 'Immagini prodotto'
        ordering = ['ordine']
    
    def __str__(self):
        return f"Immagine di {self.prodotto.nome}"


class Mulinello(Product):
    """Modello specifico per mulinelli da pesca"""
    # Caratteristiche tecniche specifiche dei mulinelli
    tipo_mulinello = models.CharField(max_length=100, choices=[
        ('SPINNING', 'Spinning'),
        ('BAITCASTING', 'Baitcasting'),
        ('SURFCASTING', 'Surfcasting'),
        ('CARPFISHING', 'Carpfishing'),
        ('TRAINA', 'Traina'),
        ('ELETTRICO', 'Elettrico'),
        ('FLY', 'Fly')
    ])
    materiale_corpo = models.CharField(max_length=100, blank=True, null=True)
    cuscinetti = models.PositiveIntegerField(blank=True, null=True, help_text='Numero di cuscinetti')
    rapporto_recupero = models.CharField(max_length=20, blank=True, null=True, help_text='Es. 6.2:1')
    peso_mulinello = models.DecimalField(max_digits=6, decimal_places=2, help_text='Peso in grammi', blank=True, null=True)
    capacita_bobina = models.CharField(max_length=100, blank=True, null=True, help_text='Es. 0.35mm/150m')
    freno_massimo = models.DecimalField(max_digits=5, decimal_places=2, help_text='Potenza freno in kg', blank=True, null=True)
    frizione = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('ANTERIORE', 'Anteriore'),
        ('POSTERIORE', 'Posteriore'),
        ('MAGNETICA', 'Magnetica')
    ])
    bobina_di_ricambio = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Mulinello'
        verbose_name_plural = 'Mulinelli'


class Canna(Product):
    """Modello specifico per canne da pesca"""
    # Caratteristiche tecniche specifiche delle canne
    tipo_canna = models.CharField(max_length=100, choices=[
        ('SPINNING', 'Spinning'),
        ('CASTING', 'Casting'),
        ('SURFCASTING', 'Surfcasting'),
        ('CARPFISHING', 'Carpfishing'),
        ('BOLOGNESE', 'Bolognese'),
        ('INGLESE', 'Inglese'),
        ('TROTA_LAGO', 'Trota Lago'),
        ('TROTA_TORRENTE', 'Trota Torrente'),
        ('FEEDER', 'Feeder'),
        ('BOMBARDA', 'Bombarda'),
        ('FISSA', 'Fissa'),
        ('TRAINA', 'Traina')
    ])
    lunghezza = models.DecimalField(max_digits=5, decimal_places=2, help_text='Lunghezza in metri')
    numero_sezioni = models.PositiveIntegerField(blank=True, null=True)
    potenza_lancio = models.CharField(max_length=50, blank=True, null=True, help_text='Es. 10-30g')
    azione = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('ULTRA_LIGHT', 'Ultra Light'),
        ('LIGHT', 'Light'),
        ('MEDIUM_LIGHT', 'Medium Light'),
        ('MEDIUM', 'Medium'),
        ('MEDIUM_HEAVY', 'Medium Heavy'),
        ('HEAVY', 'Heavy'),
        ('EXTRA_HEAVY', 'Extra Heavy')
    ])
    materiale = models.CharField(max_length=100, blank=True, null=True, help_text='Es. Carbonio, Fibra di vetro')
    ingombro = models.DecimalField(max_digits=5, decimal_places=2, help_text='Ingombro chiusa in cm', blank=True, null=True)
    anelli = models.CharField(max_length=100, blank=True, null=True)
    porta_mulinello = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Canna da pesca'
        verbose_name_plural = 'Canne da pesca'


class Esca(Product):
    """Modello specifico per esche artificiali e naturali"""
    # Caratteristiche tecniche specifiche delle esche
    tipo_esca = models.CharField(max_length=100, choices=[
        ('ARTIFICIALE', 'Artificiale'),
        ('NATURALE', 'Naturale'),
        ('VIVA', 'Viva')
    ])
    categoria_artificiale = models.CharField(max_length=100, blank=True, null=True, choices=[
        ('HARD_BAIT', 'Hard Bait'),
        ('SOFT_BAIT', 'Soft Bait'),
        ('SPOON', 'Spoon'),
        ('SPINNER', 'Spinner'),
        ('JIG', 'Jig'),
        ('POPPER', 'Popper'),
        ('STICKBAIT', 'Stickbait'),
        ('CRANKBAIT', 'Crankbait'),
        ('SWIMBAIT', 'Swimbait'),
        ('TOPWATER', 'Topwater'),
        ('ALTRO', 'Altro')
    ])
    lunghezza_esca = models.DecimalField(max_digits=5, decimal_places=2, help_text='Lunghezza in cm', blank=True, null=True)
    peso_esca = models.DecimalField(max_digits=5, decimal_places=2, help_text='Peso in grammi', blank=True, null=True)
    profondita_lavoro = models.CharField(max_length=50, blank=True, null=True, help_text='Es. 0-1m, Superficie')
    colore = models.CharField(max_length=100, blank=True, null=True)
    galleggiante = models.BooleanField(default=False)
    ancorette = models.PositiveIntegerField(blank=True, null=True, help_text='Numero di ancorette')
    rattlin = models.BooleanField(default=False, help_text='Produce suoni/vibrazioni')
    specie_target = models.CharField(max_length=255, blank=True, null=True, help_text='Es. Spigola, Trota, Black Bass')
    
    class Meta:
        verbose_name = 'Esca'
        verbose_name_plural = 'Esche'
