from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe 
from django.utils import timezone
from userauths.models import CustomUser

#-------------------------categorie de vehicule-----------------------------#
class CategoVehi(models.Model):
    cid = ShortUUIDField(unique=True, length=6, prefix='AT', alphabet="abcd1234")
    category = models.CharField(unique=True, max_length=10)
    date_saisie = models.DateField(auto_now_add=True)
    recette_defaut = models.IntegerField(default=0)
    def __str__(self):
        return self.category
 
class Vehicule(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True, related_name='user_add_veh')
    immatriculation = models.CharField(unique=True, max_length=30)
    marque = models.CharField(max_length=20)
    duree = models.IntegerField(default=0)
    image = models.ImageField(upload_to="CARS", null=True, blank=True,)
    photo_carte_grise = models.ImageField(upload_to="Photo_Carte_Grise", null=True, blank=True,)
    num_cart_grise = models.CharField(max_length=50, unique=True)
    num_Chassis = models.CharField(max_length=50, unique=True)
    date_acquisition = models.DateField()
    cout_acquisition = models.IntegerField(default=0)
    dat_edit_carte_grise = models.DateField()
    date_mis_service = models.DateField()
    category = models.ForeignKey(CategoVehi, on_delete=models.CASCADE, related_name="catego_vehicule")
    date_saisie = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.immatriculation
    @property
    def age(self):  # sourcery skip: inline-immediately-returned-variable
        import datetime
        date_nai = self.date_mis_service
        tday = datetime.date.today() 
        age = (tday.year - date_nai.year) - int((date_nai.month,tday.day ) < (date_nai.month, tday.day))
        return age

class DocumentVehicule(models.Model):
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='documents')
    nom_doc = models.CharField(max_length=100)
    image = models.ImageField(upload_to='documents_vehicules/', null=True, blank=True)
    date_saisie = models.DateField(auto_now_add=True)
    class Meta:
        ordering = ['-date_saisie']
    def __str__(self):
        return f"{self.nom_doc} - {self.vehicule.immatriculation}"

class Recette(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True, blank=True, related_name='user_add_rec')
    chauffeur = models.CharField(max_length=50)
    cpte_comptable = models.CharField(max_length=100)
    numero_fact = models.CharField(max_length=20)
    Num_piece = models.CharField(max_length=100)
    vehicule = models.ForeignKey(Vehicule, related_name="recettes", on_delete=models.CASCADE)
    montant = models.IntegerField(default=0)
    date_saisie = models.DateField()
    date = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        # Remplir automatiquement auteur_nom si l'auteur existe
        if self.auteur:
            self.auteur_nom = f"{self.auteur.username} ({self.auteur.email})"
        super().save(*args, **kwargs)
    def __str__(self): 
        return '%s ' % (self.vehicule.immatriculation)

class ChargeFixe(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True, related_name='user_add_chf')
    libelle = models.CharField(max_length=100, null=True, blank=True)
    vehicule = models.ForeignKey(Vehicule, related_name="chargefixes", on_delete=models.CASCADE)
    montant = models.IntegerField(default=0.0)
    cpte_comptable = models.CharField(max_length=100)
    Num_piece = models.CharField(max_length=100)
    Num_fact = models.CharField(max_length=100)
    date_saisie = models.DateField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self) : 
        return '%s ' % (self.vehicule.immatriculation)
    
class ChargeVariable(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True, related_name='user_add_var')
    libelle = models.CharField(max_length=100, null=True, blank=True)
    vehicule = models.ForeignKey(Vehicule, related_name="chargevariables", on_delete=models.CASCADE)
    montant = models.IntegerField(default=0.0)
    cpte_comptable = models.CharField(max_length=100)
    Num_piece = models.CharField(max_length=100)
    Num_fact = models.CharField(max_length=100)
    date_saisie = models.DateField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self) : 
        return '%s ' % (self.vehicule.immatriculation)
    
class ChargeAdminis(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True, related_name='user_add_chadm')
    libelle = models.CharField(max_length=100)
    montant = models.IntegerField(default=0.0)
    cpte_comptable = models.CharField(max_length=100)
    Num_piece = models.CharField(max_length=100)
    Num_fact = models.CharField(max_length=100)
    date_saisie = models.DateField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self) : 
        return '%s ' % (self.libelle)

class Prevision(models.Model):
    mois = models.DateField()
    montant_previs= models.IntegerField(default=0)
    def __str__(self):
        return '%s - %s' % (self.mois, self.montant_previs)
    def calculer_difference(self):
        recettes_du_mois = Recette.objects.filter(date__year=self.mois.year, date__month=self.mois.month)
        somme_recettes_du_mois = recettes_du_mois.aggregate(models.Sum('montant'))['montant__sum'] or 0
        difference = self.montant_previs - somme_recettes_du_mois
        return somme_recettes_du_mois, difference

class Billetage(models.Model):
    valeur = models.IntegerField(choices=[(10000, '10000'),  
                                          (5000, '5000'),     
                                          (2000, '2000'),    
                                          (1000, '1000'),    
                                          (500, '500'),      
                                          (200, '200'),
                                          (100, '100'), 
                                          (50, '50'), 
                                          (25, '25'),
                                          (10, '10'),           
                                          (5, '5')]
                                        )        
    nombre = models.IntegerField()
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True, related_name='bielletages')
    type = models.CharField(max_length=10, choices=[('Billet', 'Billet'), ('Pièce', 'Pièce')])
    date_saisie = models.DateField(auto_now_add=True)
    def calculer_produit(self):
        return self.valeur * self.nombre

class SoldeJour(models.Model):
    date_saisie = models.DateField(unique=True)
    montant = models.IntegerField(default=0)
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True, related_name='user_add_sold')
    date = models.DateField(auto_now_add=True)
    def __str__(self):
        return '%s - %s' % (self.date_saisie, self.montant)
    
class Encaissement(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True, related_name='user_add_enc')
    Num_piece = models.CharField(max_length=100)
    libelle = models.CharField(max_length=100)
    montant = models.IntegerField(default=0)
    date_saisie = models.DateField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):  # sourcery skip: replace-interpolation-with-fstring
        return '%s - %s' % (self.libelle, self.montant)

class Decaissement(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True, related_name='user_dec')
    Num_piece = models.CharField(max_length=100)
    libelle = models.CharField(max_length=200)
    montant = models.IntegerField(default=0)
    date_saisie = models.DateField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):  # sourcery skip: replace-interpolation-with-fstring
        return '%s - %s' % (self.libelle, self.montant)
  
class Vignette(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True, related_name='user_add_vig')
    vehicule = models.ForeignKey(Vehicule, related_name="vignettes", on_delete=models.CASCADE)
    montant = models.IntegerField(default=0)
    image = models.ImageField(upload_to="vignettes_fil", blank=True)
    date_saisie = models.DateField()
    date_proch = models.DateField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):  # sourcery skip: replace-interpolation-with-fstring
         return '%s - %s' % (self.vehicule.immatriculation, self.montant)
    @property
    def jours_vign_restant(self):
        jours_vign_restant = (self.date_proch - timezone.now().date()).days
        return jours_vign_restant

MOTIF_REPARATION=(
    ('Visite', 'Visite'),
    ('Panne', 'Panne'),
    ('Accident', 'Accident'),
)
class Reparation(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True, related_name='user_add_rep')
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="reparations")
    date_entree = models.DateTimeField()
    date_sortie = models.DateTimeField()
    motif = models.CharField(max_length=20, choices=MOTIF_REPARATION)
    image = models.ImageField(upload_to="reparation_fil", blank=True)
    num_fich = models.IntegerField()
    description = models.TextField(max_length=500, null=True, blank=True)
    montant = models.IntegerField(default=0)
    prestation = models.IntegerField(default=0)
    date_saisie = models.DateField(auto_now_add=True)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return '%s ' % (self.vehicule.immatriculation)  

LIEU_PIECE = (
    ('INTERNE', 'INTERNE'),
    ('EXTERNE', 'EXTERNE'),
)
class Piece(models.Model):
    reparation = models.ForeignKey(Reparation, on_delete=models.CASCADE, related_name="pieces")
    libelle = models.CharField(max_length=30, null=True, blank=True)
    lieu = models.CharField(max_length=20, choices=LIEU_PIECE)
    montant = models.IntegerField(default=0)
    date_saisie = models.DateField(auto_now_add=True)
    def __str__(self):
        return '%s ' % (self.libelle)
    
class PiecEchange(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name='user_piechange')
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="piechang")
    libelle = models.CharField(max_length=30, null=True, blank=True)
    lieu = models.CharField(max_length=20, choices=LIEU_PIECE)
    montant = models.IntegerField(default=0)
    date_saisie = models.DateField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return '%s ' % (self.libelle)

class Entretien(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True, related_name='user_add_ent')
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="entretiens")
    image = models.ImageField(upload_to="entretiens_fil", blank=True)
    date_Entret = models.DateTimeField()
    date_sortie = models.DateTimeField()
    date_proch = models.DateField()
    montant = models.IntegerField(default=0)
    date_saisie = models.DateField(auto_now_add=True)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.vehicule.immatriculation
    @property
    def jours_ent_restant(self):
        jours_ent_restant = (self.date_proch - timezone.now().date()).days
        return jours_ent_restant

class Autrarret(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True, related_name='user_add_aut')
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="autrarrets")
    libelle = models.CharField(max_length=50, null=True, blank=True)
    date_arret = models.DateTimeField()
    date_sortie = models.DateTimeField()
    numfich = models.CharField(max_length=100, null=True, blank=True)
    montant = models.IntegerField(default=0)
    date_saisie = models.DateField(auto_now_add=True)
    def __str__(self):
        return '%s ' % (self.vehicule.immatriculation)

class VisiteTechnique(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True, related_name='user_add_vis')
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="visites")
    date_vis = models.DateTimeField()
    date_sortie = models.DateTimeField()
    image = models.ImageField(upload_to="visites_fil", blank=True)
    date_proch= models.DateField()
    montant = models.IntegerField(default=0)
    date_saisie = models.DateField(auto_now_add=True)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.vehicule.immatriculation
    @property
    def jour_restant(self):
        jours_restant = (self.date_proch - timezone.now().date()).days
        return jours_restant
    
class Patente(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name='user_add_pat')
    vehicule = models.ForeignKey(Vehicule, related_name="patantes", on_delete=models.CASCADE)
    montant = models.IntegerField(default=0)
    image = models.ImageField(upload_to="patentes_fil", blank=True)
    date_saisie = models.DateField()
    date_proch = models.DateField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):  # sourcery skip: replace-interpolation-with-fstring
         return '%s - %s' % (self.vehicule.immatriculation, self.montant)
    @property
    def jours_pate_restant(self):
        jours_pate_restant = (self.date_proch - timezone.now().date()).days
        return jours_pate_restant
    
class Stationnement(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name='user_add_sta')
    vehicule = models.ForeignKey(Vehicule, related_name="cart_station", on_delete=models.CASCADE)
    montant = models.IntegerField(default=0)
    image = models.ImageField(upload_to="carte_station_fil", blank=True)
    date_saisie = models.DateField()
    date_proch = models.DateField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):  
        return '%s - %s' % (self.vehicule.immatriculation, self.montant)
    @property
    def jours_cartsta_restant(self):
        jours_cartsta_restant = (self.date_proch - timezone.now().date()).days
        return jours_cartsta_restant

class Assurance(models.Model):
    auteur = models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name='user_add_ass')
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="assurances")
    image = models.ImageField(upload_to="assurances_fil", blank=True)
    date_saisie = models.DateField()
    date_proch = models.DateField()
    montant = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.vehicule.immatriculation
    @property
    def jours_assu_restant(self):
        jours_assu_restant = (self.date_proch - timezone.now().date()).days
        return jours_assu_restant
