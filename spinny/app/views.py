
from rest_framework import serializers
from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Box
from .serializers import BoxSerializer, BoxFullSerializer
from .permissions import IsStaffOrReadOnly, IsOwner
from django.db.models import F, ExpressionWrapper, fields
from datetime import datetime, timedelta
from django.db.models import Avg
from django.utils import timezone
from django.core.exceptions import BadRequest

A1 = 100
V1 = 1000
L1 = 100
L2 = 50

def home(request):
    return render(request,'index.html')




class BoxList(generics.ListAPIView):
    queryset = Box.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return BoxFullSerializer
        else:
            return BoxSerializer
        
    def get_queryset(self):
        queryset = Box.objects.all()

        length_more_than = self.request.query_params.get('length_more_than')
        length_less_than = self.request.query_params.get('length_less_than')
        width_more_than = self.request.query_params.get('width_more_than')
        width_less_than = self.request.query_params.get('width_less_than')
        height_more_than = self.request.query_params.get('height_more_than')
        height_less_than = self.request.query_params.get('height_less_than')
        area_more_than = self.request.query_params.get('area_more_than')
        area_less_than = self.request.query_params.get('area_less_than')
        volume_more_than = self.request.query_params.get('volume_more_than')
        volume_less_than = self.request.query_params.get('volume_less_than')
        created_by = self.request.query_params.get('created_by')
        created_before = self.request.query_params.get('created_before')
        created_after = self.request.query_params.get('created_after')

        if length_more_than:
            queryset = queryset.filter(length__gt=length_more_than)
        if length_less_than:
            queryset = queryset.filter(length__lt=length_less_than)
        if width_more_than:
            queryset = queryset.filter(width__gt=width_more_than)
        if width_less_than:
            queryset = queryset.filter(width__lt=width_less_than)
        if height_more_than:
            queryset = queryset.filter(height__gt=height_more_than)
        if height_less_than:
            queryset = queryset.filter(height__lt=height_less_than)

        if area_more_than:
            queryset = queryset.annotate(
                calculated_area=ExpressionWrapper(
                    2 * (F('length') * F('width') + F('length') * F('height') + F('height') * F('width')),
                    output_field=fields.FloatField()
                )
            ).filter(calculated_area__gt=area_more_than)

        if area_less_than:
            queryset = queryset.annotate(
                calculated_area=ExpressionWrapper(
                    2 * (F('length') * F('width') + F('length') * F('height') + F('height') * F('width')),
                    output_field=fields.FloatField()
                )
            ).filter(calculated_area__lt=area_less_than)

        if volume_more_than:
            queryset = queryset.annotate(
                calculated_volume=ExpressionWrapper(
                    (F('length') * F('width') * F('height')),
                    output_field=fields.FloatField()
                )
            ).filter(calculated_volume__gt=volume_more_than)

        if volume_less_than:
            queryset = queryset.annotate(
                calculated_volume=ExpressionWrapper(
                    (F('length') * F('width') * F('height')),
                    output_field=fields.FloatField()
                )
            ).filter(calculated_volume__lt=volume_less_than)   
        
        if created_by:
            queryset = queryset.filter(creator__username=created_by)
        if created_before:
            queryset = queryset.filter(created_at__lt=created_before)
        if created_after:
            queryset = queryset.filter(created_at__gt=created_after)

        return queryset

class AddBox(generics.ListCreateAPIView):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def create(self, request, *args, **kwargs):
        box_data = request.data

        # Condition 1 -  Average area of all added boxes should not exceed A1
        avg_area = Box.objects.aggregate(avg_area=Avg(
            2 * (F('length') * F('width') + F('length') * F('height') + F('height') * F('width'))
        ))['avg_area'] or 0
        newArea = 2 * (float(box_data['length'])*float(box_data['width']) + float(box_data['length'])*float(box_data['height']) + float(box_data['height'])*float(box_data['width']))
        if (((avg_area + newArea)/2) > A1):
            raise BadRequest('Average area exceeds the limit A1.')

        # Condition 2 - Average volume of all boxes added by the current user shall not exceed V1
        avg_volume = Box.objects.filter(creator=self.request.user).aggregate(avg_volume=Avg(
            F('length') * F('width') * F('height')
        ))['avg_volume'] or 0
        newVolume= float(box_data['length'])*float(box_data['width'])*float(box_data['height'])
        if (((avg_volume + newVolume)/2) > V1):
            raise BadRequest("Total volume exceeds the limit V1.")
        
        # Condition 3 - Total Boxes added in a week cannot be more than L1 
        current_week_start = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
        total_boxes_week = Box.objects.filter(created_at__gte=current_week_start).count()

        if total_boxes_week >= L1:
            raise BadRequest("Total boxes added in the week exceeds the limit L1.")

        # Condition 4 - Total Boxes added in a week by a user cannot be more than L2
        total_boxes_user_week = Box.objects.filter(creator=self.request.user, created_at__gte=current_week_start).count()

        if total_boxes_user_week >= L2:
            raise BadRequest("Total boxes added by the user in the week exceeds the limit L2.")
        
        new_Box = Box.objects.create(
            creator =  request.user,
            length = float(box_data["length"]),
            width = float(box_data["width"]),
            height = float(box_data["height"])
        )
        new_Box.save()
        serializer = BoxFullSerializer(new_Box)
        return Response(serializer.data)


class UpdateBox(generics.RetrieveUpdateAPIView):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def put(self, request, pk, *args, **kwargs):
        box_data = request.data

        # Condition 1 -  Average area of all added boxes should not exceed A1
        avg_area = Box.objects.aggregate(avg_area=Avg(
            2 * (F('length') * F('width') + F('length') * F('height') + F('height') * F('width'))
        ))['avg_area'] or 0
        newArea = 2 * (float(box_data['length'])*float(box_data['width']) + float(box_data['length'])*float(box_data['height']) + float(box_data['height'])*float(box_data['width']))
        if (((avg_area + newArea)/2) > A1):
            raise BadRequest('Average area exceeds the limit A1.')

        # Condition 2 - Average volume of all boxes added by the current user shall not exceed V1
        avg_volume = Box.objects.filter(creator=self.request.user).aggregate(avg_volume=Avg(
            F('length') * F('width') * F('height')
        ))['avg_volume'] or 0
        newVolume= float(box_data['length'])*float(box_data['width'])*float(box_data['height'])
        if (((avg_volume + newVolume)/2) > V1):
            raise BadRequest("Total volume exceeds the limit V1.")
        
        # Condition 3 - Total Boxes added in a week cannot be more than L1 
        current_week_start = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
        total_boxes_week = Box.objects.filter(created_at__gte=current_week_start).count()

        if total_boxes_week >= L1:
            raise BadRequest("Total boxes added in the week exceeds the limit L1.")

        # Condition 4 - Total Boxes added in a week by a user cannot be more than L2
        total_boxes_user_week = Box.objects.filter(creator=self.request.user, created_at__gte=current_week_start).count()

        if total_boxes_user_week >= L2:
            raise BadRequest("Total boxes added by the user in the week exceeds the limit L2.")
        
        existing_box = Box.objects.get(id=pk)  # Replace 'box_id' with the actual identifier

        existing_box.length = float(box_data["length"])
        existing_box.width = float(box_data["width"])
        existing_box.height = float(box_data["height"])

        existing_box.save()
        serializer = BoxFullSerializer(existing_box)
        return Response(serializer.data)



class MyBoxList(generics.ListAPIView):
    queryset = Box.objects.all()
    serializer_class = BoxFullSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        # return Box.objects.filter(creator=self.request.user)   
        queryset = Box.objects.filter(creator=self.request.user)

        length_more_than = self.request.query_params.get('length_more_than')
        length_less_than = self.request.query_params.get('length_less_than')
        width_more_than = self.request.query_params.get('width_more_than')
        width_less_than = self.request.query_params.get('width_less_than')
        height_more_than = self.request.query_params.get('height_more_than')
        height_less_than = self.request.query_params.get('height_less_than')
        area_more_than = self.request.query_params.get('area_more_than')
        area_less_than = self.request.query_params.get('area_less_than')
        volume_more_than = self.request.query_params.get('volume_more_than')
        volume_less_than = self.request.query_params.get('volume_less_than')


        if length_more_than:
            queryset = queryset.filter(length__gt=length_more_than)
        if length_less_than:
            queryset = queryset.filter(length__lt=length_less_than)
        if width_more_than:
            queryset = queryset.filter(width__gt=width_more_than)
        if width_less_than:
            queryset = queryset.filter(width__lt=width_less_than)
        if height_more_than:
            queryset = queryset.filter(height__gt=height_more_than)
        if height_less_than:
            queryset = queryset.filter(height__lt=height_less_than)

        if area_more_than:
            queryset = queryset.annotate(
                calculated_area=ExpressionWrapper(
                    2 * (F('length') * F('width') + F('length') * F('height') + F('height') * F('width')),
                    output_field=fields.FloatField()
                )
            ).filter(calculated_area__gt=area_more_than)

        if area_less_than:
            queryset = queryset.annotate(
                calculated_area=ExpressionWrapper(
                    2 * (F('length') * F('width') + F('length') * F('height') + F('height') * F('width')),
                    output_field=fields.FloatField()
                )
            ).filter(calculated_area__lt=area_less_than)

        if volume_more_than:
            queryset = queryset.annotate(
                calculated_volume=ExpressionWrapper(
                    (F('length') * F('width') * F('height')),
                    output_field=fields.FloatField()
                )
            ).filter(calculated_volume__gt=volume_more_than)

        if volume_less_than:
            queryset = queryset.annotate(
                calculated_volume=ExpressionWrapper(
                    (F('length') * F('width') * F('height')),
                    output_field=fields.FloatField()
                )
            ).filter(calculated_volume__lt=volume_less_than)   

        return queryset
    
    
    
class DeleteBox(generics.RetrieveDestroyAPIView):
    queryset = Box.objects.all()
    serializer_class = BoxFullSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly, IsOwner]

    def get_queryset(self):
        return Box.objects.filter(creator=self.request.user)