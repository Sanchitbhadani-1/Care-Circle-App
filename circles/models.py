from django.db import models
from django.conf import settings

#Create the CareCircle model
class CareCircle(models.Model):

    #Set the name of the circle
    name = models.CharField(max_length=100)

    #Create ownership capabilities within the circle
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, #If owner gets deleted, circle is deleted
        related_name="owned_circles", #Be able to find out all cirlce a user is in
    )
    created_at = models.DateTimeField(auto_now_add=True) #Add a timestamp to circles

    #Return the name of a circle
    def __str__(self):
        return self.name
