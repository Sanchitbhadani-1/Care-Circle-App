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

class Membership(models.Model): #Defines the membership model
    
    #The different roles a user can be in a circle
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("caregiver", "Caregiver"),
        ("senior", "Senior"),
    ]

    #Connects the user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    
    #Connects the circle with the user
    circle = models.ForeignKey(
        CareCircle,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    #Assigns user's role in the circle
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="caregiver")

    class Meta:
        unique_together = ("user", "circle")   # no duplicate user+circle rows

    def __str__(self):
        return f"{self.user.email} — {self.role} in {self.circle.name}"
