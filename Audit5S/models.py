from enum import unique
from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth.models import (BaseUserManager , AbstractBaseUser,)
from django.contrib.auth.models import Permission
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import  MaxValueValidator, MinValueValidator
from rest_framework import permissions

class UserManager (BaseUserManager):
    def create_user (self,username, email, nom , prenom , numtel , photo,departement,role, password=None,is_staff=True,is_admin=False):
        if not email:
            raise ValueError('L\'utilisateur doit avoir une adresse email')
        
        user = self.model(
            username = username,
            email = self.normalize_email(email),
            nom = nom,
            prenom = prenom,
            numtel = numtel,
            photo = photo,
            departement = departement,
            role = role,
        )
        user.set_password(password)
        user.staff = is_staff
        user.admin = is_admin
        user.save(using=self._db)
        return user


    def create_superuser (self,username,email, nom , prenom , numtel , photo,departement,role, password=None):
        user = self.create_user(
            username = username,
            email=self.normalize_email(email),
            password=password,
            nom = nom,
            prenom = prenom,
            numtel = numtel,
            photo = photo,
            departement = departement,
            role = 1,
            
            is_admin=True,
            is_staff=True,
        )
        user.save(using=self._db)
        return user

class User (AbstractBaseUser):

    ADMINISTRATEUR = 1
    AUDITEUR = 2
   
    ROLE_CHOICES = (
        (ADMINISTRATEUR, 'Administrateur'),
        (AUDITEUR, 'Auditeur'),
        )
    
    email = models.EmailField(verbose_name='email address',max_length=255,unique=False,)
    username = models.CharField(max_length=20,unique=True, error_messages={ "max_length":"Le username est trop long"})
    nom = models.CharField(max_length=50,null=True, error_messages={ "max_length":"Le nom est trop long"})
    prenom = models.CharField(max_length=50,null=True, error_messages={"max_length":"Le prenom est trop long"})
    departement = models.CharField(blank=True,max_length=50,null=True, error_messages={"max_length":"Le nom du département est trop long"})
    numtel = models.CharField(max_length=15,null=False, blank=False)
    photo = models.ImageField(upload_to='static/Photo_auditeur',null=True,blank=True)
    
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True,default=2)
    admin=models.BooleanField(default=False)
    staff=models.BooleanField(default=True)
    objects = UserManager()
    
    @property
    def is_staff(self):
       return self.is_admin

    def has_perm(self, perm, obj=None):
       return self.is_admin

    def has_module_perms(self, app_label):
       return self.is_admin
       
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nom','prenom','email','numtel' , 'photo','departement','groups','role']
     
    #class Meta:
    #    permissions=(("view_zone","Can view zones"),
    #    )
    
    def __str__(self):
        return str(self.prenom) +''+ str(self.nom)
    
    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin 
    
    @property
    def is_admin(self):
        if self.role == 1 :
            
            return True
        else:
            return False

    def auditeurs():
      l=[]
      auditeurs=User.objects.filter(role=2)
      
      for auditeur in auditeurs :
        
        e=[auditeur.username,auditeur.username]
        k=tuple(e)
        l.append(k)
       
      return tuple(l) ;    

    def is_auditeur(self):
        if self.role == 2 :
            return True
        else:
            return False


class Responsable (models.Model):

    photo = models.ImageField(upload_to='static/Photo_responsable')
    nom = models.CharField(max_length=50, error_messages={ "max_length":"Le nom est trop long"})
    prenom = models.CharField(max_length=50, error_messages={"max_length":"Le prenom est trop long"})
    email = models.EmailField(verbose_name='email address',max_length=255,)
    numtel = models.CharField(max_length=12)
    
    def __str__(self):
        return ""+self.nom+" "+self.prenom

    

class Zone(models.Model):

    responsable = models.ForeignKey(Responsable,on_delete=models.CASCADE )
    nom = models.CharField(max_length=30)

    def __str__(self):
        return "  %s" % self.nom
     

class Audit(models.Model):
    

    
    date = models.DateField(null=True)
    tauxRespect = models.FloatField(null=True,validators=[MinValueValidator(0),MaxValueValidator(100)])
    tauxMin = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)],null=True)
    zone = models.ForeignKey(Zone,on_delete=models.CASCADE)
    auditeur = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return " Audit realisé en  " + str(self.date) +"    " 



             
class Categorie(models.Model):
    
    nom = models.TextField()

    def __str__(self):
      return " %s"%self.nom
      
class PlanAction(models.Model):

    audit = models.OneToOneField(Audit,on_delete=models.CASCADE,)

    def __str__(self):
      return " ce plan d'action concerne l'audit N° %d" % self.audit.id        

class Action(models.Model):
    
    probleme =models.TextField(blank=True)
    cause=models.TextField(blank=True)
    actionAfaire=models.TextField(blank=True)
    delai=models.DateField()
    tauxEfficacite=models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(100)])
    planAction = models.ForeignKey(PlanAction, on_delete=models.CASCADE)
    
    

      

class Standard(models.Model):

    description=models.TextField(max_length=300)
    photoStandard = models.CharField(blank=True,max_length=100)
    date_de_creation=models.DateField(auto_now_add=True)
    zone=models.ManyToManyField(Zone)
    valstandard=models.IntegerField(null=True,validators=[MinValueValidator(0),MaxValueValidator(1)])
    categorie=models.ForeignKey(Categorie,on_delete=models.CASCADE)
    
    def __str__(self):
        return "%s" %self.description

class Score(models.Model):
    
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE)
    standard = models.OneToOneField(Standard,on_delete=models.CASCADE)
    valeur=models.IntegerField(blank=True,validators=[MinValueValidator(0),MaxValueValidator(1)])
        
    

    






            
            
      
     

