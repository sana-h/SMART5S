# Create your views here.
from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.serializers import Serializer
from audit5S.models import *
from .serializers import *   
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated, IsAuthenticatedOrReadOnly, BasePermission, IsAdminUser, DjangoModelPermissions
from rest_framework import status


#permissions classes
class AuditUserWritePermission(BasePermission):
    message = 'update,delete,audit/create actions of audit is restricted to his own auditeur only.'

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True

        return obj.auditeur == request.user
class AuditUserCreatePermission(BasePermission):
    message = 'Creating audits is restricted to auditeurs only.'

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True
        elif request.user.role==2: 
            return True   
        else:
            return False
                
class UserWritePermission(BasePermission):
    message = 'create,update,delete  zones/categories/standards/responsable is restricted to admin only.'

    def has_permission(self, request,view):

        if request.method in SAFE_METHODS:
            return True
        elif request.user.role==1:
            return True
        else :
            return False    
#views classes
#creating and listing audits
class AuditList(generics.ListCreateAPIView,):
    queryset = Audit.objects.all()
    serializer_class = AuditSerializer
    permission_classes = [AuditUserCreatePermission]
    authentication_classes=(TokenAuthentication,)


#afficher le responsable d'une zone d'un audit
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def azr(request,pk):
    
    if request.method == 'GET':
        audit = Audit.objects.get(id=pk)
        zone =audit.zone
        responsable=zone.responsable
        serializer = ResponsableSerializer(responsable, many=False)
        return Response(serializer.data) 
#afficher/modifier/supprimer un audit
class AuditDetails(generics.RetrieveUpdateDestroyAPIView,AuditUserWritePermission):
    permission_classes = [AuditUserWritePermission]
    queryset = Audit.objects.all()
    serializer_class = AuditSerializer
    authentication_classes=(TokenAuthentication,)
    
#afficher/creer/modifier/supprimer les actions d'un audit
class AuditActionList (generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        permission_classes = [AuditUserWritePermission]
        authentication_classes=(TokenAuthentication,)
        a1 = Audit.objects.get(id=self.kwargs["pk"])
        plan= PlanAction.objects.all()
        for p in plan :
            if p.audit ==a1:
                queryset2=Action.objects.filter(planAction=p)
                break    
        return queryset2
    serializer_class = ActionSerializer

#afficher la zone d'un audit
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def zone(request,pk):
    
    if request.method == 'GET':
        audit = Audit.objects.get(id=pk)
        zone =audit.zone
        serializer = ZoneSerializer(zone, many=False)
        return Response(serializer.data)

#afficher le responsable d'une zone d'un audit
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def azr(request,pk):
    
    if request.method == 'GET':
        audit = Audit.objects.get(id=pk)
        zone =audit.zone
        responsable=zone.responsable
        serializer = ResponsableSerializer(responsable, many=False)
        return Response(serializer.data)    

#les classes des actions
#afficher et creation les actions
class ActionList(generics.ListCreateAPIView):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [AuditUserWritePermission]
    authentication_classes=(TokenAuthentication,)
#afficher/modifier/creer/modifier les actions d'un audit
class ActionDetails(generics.RetrieveUpdateDestroyAPIView,AuditUserWritePermission):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    permission_classes = [AuditUserWritePermission]
    authentication_classes=(TokenAuthentication,)
    
    
#les classes des zones
#afficher et creer tous les zones
class ZoneList(generics.ListCreateAPIView):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [UserWritePermission]
    authentication_classes=(TokenAuthentication,)
#afficher/modifier/creer/modifier/supprimer une zone
class ZoneDetails(generics.RetrieveUpdateDestroyAPIView,UserWritePermission):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [UserWritePermission]
    authentication_classes=(TokenAuthentication,)
    
      
#afficher/modifier/supprimer/creer le responsable d'une zone
class ZoneResponsableList (generics.RetrieveUpdateDestroyAPIView,UserWritePermission):                    
    def get_queryset(self):
        queryset = Responsable.objects.filter(zone=self.kwargs["pk"])
        return queryset    
    serializer_class = ResponsableSerializer
    permission_classes=UserWritePermission
    authentication_classes=(TokenAuthentication,)
#afficher et creer tous les standards
class StandardList(generics.ListCreateAPIView,UserWritePermission):
    queryset = Standard.objects.all()
    serializer_class = StandardSerializer
    permission_classes=UserWritePermission
    authentication_classes=(TokenAuthentication,)

#afficher et creer tous les categories
class CategorieList(generics.ListCreateAPIView,UserWritePermission):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes=UserWritePermission
    authentication_classes=(TokenAuthentication,)

#afficher/modifier/supprimer une categorie
class CategorieDetails(generics.RetrieveUpdateDestroyAPIView,UserWritePermission ):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes=UserWritePermission
    authentication_classes=(TokenAuthentication,)
